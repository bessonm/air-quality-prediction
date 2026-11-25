import csv
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from io import StringIO
from pathlib import Path
from types import TracebackType
from uuid import uuid4

import pandas as pd
import requests
from dotenv import find_dotenv, load_dotenv

type QueryValue = str | int | bool | None

logger = logging.getLogger(__name__)


class GeodairClient:
    """Accès aux référentiels et mesures de Geod'air.

    La clé GEODAIR_API_KEY est chargée depuis .env, recherché depuis le
    répertoire courant et ses parents, ou depuis ``env_path``. Une variable
    d'environnement existante reste prioritaire. Aucun appel réseau n'est
    effectué à l'initialisation.

    ``timeout`` limite chaque requête HTTP (secondes d'inactivité réseau).
    ``max_download_attempts`` borne l'attente d'un export, avec une pause de
    ``poll_interval`` secondes entre les réponses d'attente (412, ainsi que
    404 après une génération réussie). Utiliser le client dans
    un bloc ``with`` ou appeler ``close()`` pour libérer sa session HTTP.

    ``min_request_interval`` espace toutes les requêtes de cette instance
    (5 secondes après la fin de la précédente). Les 429 sont réessayés jusqu'à
    ``max_rate_limit_retries`` fois : Retry-After est prioritaire, sinon le
    délai vaut rate_limit_backoff * 2**tentative (30, 60, 120 s par défaut).
    Ces attentes s'ajoutent au temps de traitement ; timeout n'est pas un
    délai global. Utiliser une seule instance, de manière séquentielle.
    """

    BASE_URL = "https://www.geodair.fr/api-ext"

    def __init__(
            self,
            *,
            env_path: str | Path | None = None,
            timeout: float = 30.0,
            poll_interval: float = 5.0,
            max_download_attempts: int = 30,
            min_request_interval: float = 5.0,
            max_rate_limit_retries: int = 3,
            rate_limit_backoff: float = 30.0,
    ) -> None:
        if timeout <= 0 or poll_interval < 0 or max_download_attempts < 1:
            raise ValueError("Délais invalides ou nombre de tentatives inférieur à 1.")
        if min_request_interval < 0 or rate_limit_backoff <= 0:
            raise ValueError("Intervalle négatif ou délai de reprise non positif.")
        if (
            isinstance(max_rate_limit_retries, bool)
            or not isinstance(max_rate_limit_retries, int)
            or max_rate_limit_retries < 0
        ):
            raise ValueError("max_rate_limit_retries doit être un entier positif ou nul.")
        load_dotenv(
            dotenv_path=env_path if env_path is not None else find_dotenv(usecwd=True),
            override=False,
        )
        api_key = os.getenv("GEODAIR_API_KEY", "").strip()
        if not api_key:
            raise ValueError("GEODAIR_API_KEY doit être définie dans .env ou l'environnement.")

        self.timeout = timeout
        self.poll_interval = poll_interval
        self.max_download_attempts = max_download_attempts
        self.min_request_interval = min_request_interval
        self.max_rate_limit_retries = max_rate_limit_retries
        self.rate_limit_backoff = rate_limit_backoff
        self._next_request_at = 0.0
        self._session = requests.Session()
        self._session.headers.update(
            {"apikey": api_key, "Accept": "text/csv; charset=UTF-8"}
        )

    def close(self) -> None:
        """Fermer la session HTTP."""
        self._session.close()

    def __enter__(self) -> "GeodairClient":
        """Ouvrir le contexte d'utilisation du client."""
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        """Fermer la session, même lorsqu'une exception survient."""
        self.close()

    def _get(
            self,
            path: str,
            params: dict[str, QueryValue],
            *,
            headers: dict[str, str] | None = None,
            allowed_statuses: tuple[int, ...] = (),
    ) -> requests.Response:
        """Encoder les filtres et vérifier le statut de la réponse HTTP.

        Les en-têtes fournis remplacent ceux de même nom dans la session ;
        les autres, notamment apikey, sont conservés.
        Les statuts explicitement autorisés sont traités par l'appelant.
        """
        query = {
            key: str(value).lower() if isinstance(value, bool) else value
            for key, value in params.items()
            if value is not None
        }
        for retry in range(self.max_rate_limit_retries + 1):
            delay = self._next_request_at - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            try:
                response = self._session.get(
                    f"{self.BASE_URL}{path}", params=query, timeout=self.timeout,
                    headers=headers, allow_redirects=False,
                )
            finally:
                self._next_request_at = time.monotonic() + self.min_request_interval
            if response.status_code != 429:
                break
            delay = self._rate_limit_delay(response, retry)
            self._next_request_at = max(self._next_request_at, time.monotonic() + delay)
            if retry == self.max_rate_limit_retries:
                response.raise_for_status()
            logger.warning(
                "Geod'air 429 sur %s : nouvelle tentative %s/%s dans %.1f s.",
                path, retry + 1, self.max_rate_limit_retries,
                max(delay, self.min_request_interval),
            )
            response.close()
        # Ne pas transmettre la clé API à une éventuelle cible de redirection.
        if 300 <= response.status_code < 400:
            raise requests.HTTPError("Redirection Geod'air inattendue.", response=response)
        if response.status_code not in allowed_statuses:
            response.raise_for_status()
        return response

    def _rate_limit_delay(self, response: requests.Response, retry: int) -> float:
        """Lire Retry-After (secondes ou date HTTP), sinon attendre exponentiellement."""
        value = response.headers.get("Retry-After", "").strip()
        if value.isascii() and value.isdigit():
            return float(value)
        if value:
            try:
                deadline = parsedate_to_datetime(value)
                if deadline.tzinfo is None:
                    deadline = deadline.replace(tzinfo=timezone.utc)
                return max(0.0, (deadline - datetime.now(timezone.utc)).total_seconds())
            except (ValueError, TypeError, OverflowError):
                pass
        return self.rate_limit_backoff * 2 ** retry

    @staticmethod
    def _read_csv(response: requests.Response) -> pd.DataFrame:
        """Lire un CSV UTF-8 en détectant son séparateur, sans typer ses valeurs."""
        if response.status_code == 204 or not response.content.strip():
            return pd.DataFrame()
        return pd.read_csv(
            StringIO(response.content.decode("utf-8-sig")),
            sep=None,
            engine="python",
            dtype=str,
            keep_default_na=False,
        )

    def _export(
            self, resource: str, params: dict[str, QueryValue], *, avance: bool
    ) -> pd.DataFrame:
        """Télécharger un export de référentiel standard ou avancé."""
        suffix = "export-avance" if avance else "export"
        response_csv = self._get(f"/{resource}/{suffix}", params)
        return self._read_csv(response_csv)

    def get_stations(
            self,
            *,
            date_debut: str | None = None,
            date_fin: str | None = None,
            commune: str | None = None,
            unite_urbaine: str | None = None,
            departement: str | None = None,
            region: str | None = None,
            zas: str | None = None,
            typologie: str | None = None,
            reglementaire: bool | None = None,
            avance: bool = False,
    ) -> pd.DataFrame:
        """Récupérer les stations et leurs métadonnées, dates au format YYYY-MM-DD.

        Les filtres géographiques attendent les codes de l'API. Renseigner
        ``reglementaire`` sélectionne automatiquement l'export avancé.
        Le Swagger ne prévoit pas de filtre par code station sur cet endpoint.
        """
        return self._export("station", {
            "dateDebut": date_debut, "dateFin": date_fin, "commune": commune,
            "uniteUrbaine": unite_urbaine, "departement": departement,
            "region": region, "zas": zas, "typologie": typologie,
            "reglementaire": reglementaire,
        }, avance=avance or reglementaire is not None)

    def get_sampling_points(
            self,
            *,
            code_station: str | None = None,
            date_debut: str | None = None,
            date_fin: str | None = None,
            reglementaire: bool | None = None,
            avance: bool = False,
    ) -> pd.DataFrame:
        """Récupérer les métadonnées des points de prélèvement d'une station.

        Les dates sont au format YYYY-MM-DD. ``code_station`` est un code FR.
        ``reglementaire`` sélectionne automatiquement l'export avancé.
        """
        return self._export("pointdeprelevement", {
            "code_station": code_station, "dateDebut": date_debut,
            "dateFin": date_fin, "reglementaire": reglementaire,
        }, avance=avance or reglementaire is not None)

    def get_pollutants(self, *, avance: bool = False) -> pd.DataFrame:
        """Récupérer les codes, noms et unités des polluants."""
        return self._export("polluant", {}, avance=avance)

    def get_pollutant_families(self, *, avance: bool = False) -> pd.DataFrame:
        """Récupérer les identifiants des familles de polluants."""
        return self._export("famille-polluant", {}, avance=avance)

    def get_data_types(
            self, codes_polluants: str, *, avance: bool = False
    ) -> pd.DataFrame:
        """Récupérer les types de statistiques et granularités disponibles.

        ``codes_polluants`` est transmis tel quel : le Swagger ne précise pas
        le séparateur pour plusieurs codes. Un code unique, par exemple "03",
        est documenté. Utiliser la colonne Identifiant comme ``type_donnee``.
        """
        return self._export(
            "type-donnees", {"codes_polluants": codes_polluants}, avance=avance
        )

    def get_measurements(
            self,
            date_debut: str,
            date_fin: str,
            type_donnee: str,
            *,
            polluant: str | None = None,
            famille_polluant: int | None = None,
            station: str | None = None,
            departement: str | None = None,
            region: str | None = None,
            zas: str | None = None,
            typologie: str | None = None,
            influence: int | None = None,
            date_calcul: bool | None = None,
            reglementaire: bool | None = None,
            avance: bool = False,
    ) -> pd.DataFrame:
        """Générer puis télécharger les mesures d'une période.

        Dates : dd/MM/YYYY hh:mm. ``type_donnee`` définit la granularité
        (exemple documenté : "a1" pour la moyenne horaire). Un ``polluant``
        ou une ``famille_polluant`` est obligatoire. Le Swagger accepte un
        code station et un code polluant par requête ; pour plusieurs codes,
        appeler cette méthode pour chaque sélection.

        ``date_calcul`` demande la date d'insertion dans le CSV.
        ``reglementaire`` sélectionne automatiquement l'export avancé.
        Après génération, les réponses 404 et 412 du téléchargement sont
        réessayées : le serveur peut renvoyer 404 avant que le CSV soit prêt.
        Une attente épuisée lève requests.Timeout. Les 429 suivent la politique
        de temporisation du client ; les autres erreurs HTTP sont propagées.
        """
        response = self._request_measurements({
            "date_debut": date_debut, "date_fin": date_fin,
            "type_donnee": type_donnee, "polluant": polluant,
            "famille_polluant": famille_polluant, "station": station,
            "departement": departement, "region": region, "zas": zas,
            "typologie": typologie, "influence": influence,
            "date_calcul": date_calcul, "reglementaire": reglementaire,
        }, avance=avance)
        return self._read_csv(response)

    def download_measurements_csv(
            self,
            date_debut: str,
            date_fin: str,
            type_donnee: str,
            *,
            directory: str | Path = "data/raw/geodair",
            filename: str | None = None,
            polluant: str | None = None,
            famille_polluant: int | None = None,
            station: str | None = None,
            departement: str | None = None,
            region: str | None = None,
            zas: str | None = None,
            typologie: str | None = None,
            influence: int | None = None,
            date_calcul: bool | None = None,
            reglementaire: bool | None = None,
            avance: bool = False,
    ) -> Path:
        """Enregistrer le CSV brut des mesures et retourner son chemin absolu.

        Les filtres et formats de dates sont ceux de get_measurements.
        Le répertoire est créé si nécessaire ; un chemin relatif est résolu
        depuis le répertoire courant (celui du kernel dans un notebook).
        Sans filename, un nom unique est généré. Un fichier existant n'est
        jamais écrasé (FileExistsError). Une réponse 204 crée un fichier vide.
        Le contenu est écrit tel que reçu, sans passage par pandas.
        """
        if filename is None:
            filename = f"geodair_{uuid4().hex}.csv"
        if not filename or Path(filename).name != filename or filename in {".", ".."}:
            raise ValueError("filename doit être un nom de fichier sans répertoire.")
        destination = Path(directory).expanduser().resolve() / filename
        if destination.exists():
            raise FileExistsError(destination)
        response = self._request_measurements({
            "date_debut": date_debut, "date_fin": date_fin,
            "type_donnee": type_donnee, "polluant": polluant,
            "famille_polluant": famille_polluant, "station": station,
            "departement": departement, "region": region, "zas": zas,
            "typologie": typologie, "influence": influence,
            "date_calcul": date_calcul, "reglementaire": reglementaire,
        }, avance=avance)
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._write_bytes(destination, response.content)
        return destination

    def download_measurements_chunked_csv(
            self,
            date_debut: str,
            date_fin: str,
            type_donnee: str,
            *,
            chunk_days: int = 31,
            resume: bool = True,
            resume_from: str | Path | None = None,
            directory: str | Path = "data/raw/geodair",
            filename: str | None = None,
            polluant: str | None = None,
            famille_polluant: int | None = None,
            station: str | None = None,
            departement: str | None = None,
            region: str | None = None,
            zas: str | None = None,
            typologie: str | None = None,
            influence: int | None = None,
            date_calcul: bool | None = None,
            reglementaire: bool | None = None,
            avance: bool = False,
    ) -> Path:
        """Télécharger une période par morceaux, puis concaténer les CSV.

        Dates au format dd/MM/YYYY hh:mm ; chunk_days est un entier positif.
        Les intervalles sont contigus : la fin d'un morceau est le début du
        suivant. Les filtres sont ceux de get_measurements. Aucune ligne
        n'est dédupliquée et aucune moyenne n'est calculée.

        Les CSV bruts sont conservés dans un sous-dossier stable *_chunks.
        Avec resume=True, relancer les mêmes paramètres reprend les morceaux
        manquants. Un manifeste vérifie la période, les filtres et chunk_days.
        Le nom par défaut dépend de ces paramètres et reste stable.
        resume_from permet de choisir un ancien dossier *_chunks sans manifeste :
        l'appelant doit garantir qu'il provient des mêmes filtres et du même
        découpage. Les anciens CSV sont vérifiés avant leur réutilisation.
        Le fichier final contient un seul en-tête, en UTF-8 avec BOM et avec
        le séparateur point-virgule. Les valeurs restent des chaînes.
        Un Path absolu est retourné ; aucun fichier existant n'est écrasé.
        Si un appel échoue, les morceaux déjà téléchargés restent disponibles
        et aucun fichier final n'est publié. Réduire chunk_days si un morceau
        dépasse encore la limite de lignes de l'API. Les erreurs 429 sont réessayées
        sur la même requête, selon la politique du client.
        """
        if isinstance(chunk_days, bool) or not isinstance(chunk_days, int) or chunk_days < 1:
            raise ValueError("chunk_days doit être un entier strictement positif.")

        date_format = "%d/%m/%Y %H:%M"
        start = datetime.strptime(date_debut, date_format)
        end = datetime.strptime(date_fin, date_format)

        if start >= end:
            raise ValueError("date_debut doit précéder date_fin.")

        if not polluant and famille_polluant is None:
            raise ValueError("Renseigner polluant ou famille_polluant.")

        settings = {
            "date_debut": start.strftime(date_format),
            "date_fin": end.strftime(date_format),
            "chunk_days": chunk_days, "type_donnee": type_donnee,
            "polluant": polluant, "famille_polluant": famille_polluant,
            "station": station, "departement": departement, "region": region,
            "zas": zas, "typologie": typologie, "influence": influence,
            "date_calcul": date_calcul, "reglementaire": reglementaire,
            "avance": avance,
        }
        if filename is None:
            identifier = hashlib.sha256(
                json.dumps(settings, sort_keys=True).encode("utf-8")
            ).hexdigest()[:16]
            filename = f"geodair_{identifier}.csv"

        if not filename or Path(filename).name != filename or filename in {".", ".."}:
            raise ValueError("filename doit être un nom de fichier sans répertoire.")

        destination = Path(directory).expanduser().resolve() / filename

        if destination.exists():
            raise FileExistsError(destination)

        chunks_directory = (
            Path(resume_from).expanduser().resolve() if resume_from is not None
            else destination.parent / f"{destination.stem}_chunks"
        )
        intervals: list[tuple[datetime, datetime, Path]] = []
        cursor = start
        while cursor < end:
            stop = (
                end if chunk_days > (end - cursor).days
                else cursor + timedelta(days=chunk_days)
            )
            intervals.append((cursor, stop, chunks_directory / f"{cursor:%Y%m%d%H%M}_{stop:%Y%m%d%H%M}.csv"))
            cursor = stop
        self._prepare_resume(
            chunks_directory, settings, [path for _, _, path in intervals],
            resume=resume, allow_legacy=resume_from is not None,
        )
        chunks: list[Path] = []

        for start, stop, chunk_path in intervals:
            if chunk_path.exists():
                logger.info("Morceau déjà téléchargé : %s", chunk_path.name)
                chunks.append(chunk_path)
                continue
            logger.info("Téléchargement du morceau %s", chunk_path.name)
            chunk = self.download_measurements_csv(
                date_debut=start.strftime(date_format),
                date_fin=stop.strftime(date_format),
                type_donnee=type_donnee,
                directory=chunks_directory,
                filename=f"{start:%Y%m%d%H%M}_{stop:%Y%m%d%H%M}.csv",
                polluant=polluant,
                famille_polluant=famille_polluant,
                station=station,
                departement=departement,
                region=region,
                zas=zas,
                typologie=typologie,
                influence=influence,
                date_calcul=date_calcul,
                reglementaire=reglementaire,
                avance=avance,
            )
            chunks.append(chunk)

        destination.parent.mkdir(parents=True, exist_ok=True)
        self._merge_csv_files(chunks, destination)
        return destination

    @staticmethod
    def _write_bytes(destination: Path, content: bytes) -> None:
        """Publier un fichier complet sans écraser une destination existante."""
        temporary = destination.with_name(f".{destination.name}.{uuid4().hex}.part")
        try:
            with temporary.open("xb") as output:
                output.write(content)
            os.link(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)

    def _prepare_resume(
        self, directory: Path, settings: dict[str, QueryValue], expected: list[Path],
        *, resume: bool, allow_legacy: bool,
    ) -> None:
        """Vérifier les paramètres et les anciens morceaux avant tout appel réseau."""
        if allow_legacy and (not resume or not directory.is_dir()):
            raise ValueError("resume_from exige resume=True et un dossier existant.")
        if directory.exists() and not resume:
            raise FileExistsError(directory)
        directory.mkdir(parents=True, exist_ok=True)
        manifest = directory / "request.json"
        if manifest.exists():
            if json.loads(manifest.read_text(encoding="utf-8")) != settings:
                raise ValueError("Le dossier de reprise correspond à d'autres paramètres.")
        else:
            existing = set(directory.glob("*.csv"))
            if existing and not allow_legacy:
                raise ValueError("Dossier sans manifeste : utiliser explicitement resume_from.")
            if existing - set(expected):
                raise ValueError("Les anciens CSV ne correspondent pas au découpage demandé.")
            # Les anciennes versions écrivaient directement la destination :
            # contrôler la structure avant d'adopter ces fichiers.
            for path in sorted(existing):
                self._validate_saved_csv(path)
            self._write_bytes(
                manifest, json.dumps(settings, indent=2, ensure_ascii=False).encode("utf-8")
            )

    @staticmethod
    def _validate_saved_csv(path: Path) -> None:
        """Vérifier la structure d'un ancien CSV, sans modifier ses valeurs."""
        with path.open(encoding="utf-8-sig", newline="") as source:
            sample = source.read(8192)
            if not sample.strip():
                return  # Une réponse 204 pouvait produire un fichier vide.
            dialect = csv.Sniffer().sniff(sample, delimiters=";,\t|")
            source.seek(0)
            reader = csv.reader(source, dialect, strict=True)
            header = next(reader)
            for row in reader:
                if len(row) != len(header):
                    raise ValueError(f"CSV incomplet ou mal formé : {path}")

    @staticmethod
    def _merge_csv_files(sources: list[Path], destination: Path) -> None:
        """Assembler les CSV en flux et publier le résultat une fois complet.

        Les en-têtes doivent être identiques ; les fichiers vides sont ignorés.
        Un fichier temporaire évite d'exposer un résultat partiel. Le lien
        final est créé sans écraser un fichier qui serait apparu entre-temps.
        """
        temporary = destination.with_name(f".{destination.name}.{uuid4().hex}.part")
        try:
            with temporary.open("x", encoding="utf-8-sig", newline="") as output:
                writer = csv.writer(output, delimiter=";")
                header: list[str] | None = None
                for source in sources:
                    with source.open(encoding="utf-8-sig", newline="") as input_file:
                        sample = input_file.read(8192)
                        if not sample.strip():
                            continue
                        dialect = csv.Sniffer().sniff(sample, delimiters=";,\t|")
                        input_file.seek(0)
                        reader = csv.reader(input_file, dialect)
                        current_header = next(reader)
                        if header is None:
                            header = current_header
                            writer.writerow(header)
                        elif current_header != header:
                            raise ValueError(f"Colonnes CSV incompatibles dans {source}.")
                        writer.writerows(reader)
            os.link(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)

    def _request_measurements(
            self, params: dict[str, QueryValue], *, avance: bool
    ) -> requests.Response:
        """Générer un export de mesures et récupérer sa réponse brute."""
        if not params.get("polluant") and params.get("famille_polluant") is None:
            raise ValueError("Renseigner polluant ou famille_polluant.")
        advanced = avance or params.get("reglementaire") is not None
        suffix = "export-avance" if advanced else "export"
        response = self._get(f"/statistique/{suffix}", params)
        export_id = response.text.strip()
        if not export_id:
            raise ValueError("Geod'air n'a pas renvoyé d'identifiant d'export.")
        return self._download_response(export_id, retry_not_found=True)

    def download_export(
            self, export_id: str, *, retry_not_found: bool = False
    ) -> pd.DataFrame:
        """Télécharger un export avec une attente bornée sur le statut 412.

        ``retry_not_found`` autorise aussi les nouvelles tentatives sur 404
        pour un identifiant venant d'être généré. get_measurements l'active
        automatiquement ; un appel direct conserve une erreur 404 immédiate.
        Un statut 204 produit un DataFrame vide. Les 429 suivent la politique
        de temporisation du client. Les autres erreurs HTTP sont propagées
        immédiatement. L'attente épuisée lève requests.Timeout.
        """
        return self._read_csv(
            self._download_response(export_id, retry_not_found=retry_not_found)
        )

    def _download_response(
            self, export_id: str, *, retry_not_found: bool
    ) -> requests.Response:
        """Attendre un export et retourner sa réponse HTTP sans conversion."""
        pending_statuses = (412, 404) if retry_not_found else (412,)
        for attempt in range(self.max_download_attempts):
            response = self._get(
                "/download",
                {"id": export_id},
                headers={"Accept": "application/octet-stream"},
                allowed_statuses=pending_statuses,
            )
            if response.status_code not in pending_statuses:
                return response
            if attempt + 1 < self.max_download_attempts:
                time.sleep(self.poll_interval)
        raise requests.Timeout(
            "L'export Geod'air n'est pas prêt après "
            f"{self.max_download_attempts} tentatives.",
            response=response,
        )
