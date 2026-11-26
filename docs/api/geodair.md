# Geod'air

- [https://www.geodair.fr/donnees/api](https://www.geodair.fr/donnees/api)
- [www.geodair.fr/api-ext](www.geodair.fr/api-ext)

## Polluants disponibles

| Code du polluant | Nom court du polluant | Libellé                                   | Unité de concentration |
|------------------|-----------------------|-------------------------------------------|------------------------|
| 01               | SO₂                   | Dioxyde de soufre                         | μg-m3                  |
| 03               | NO₂                   | Dioxyde d’azote                           | μg-m3                  |
| 04               | CO                    | Monoxyde de carbone                       | mg-m3                  |
| 08               | O₃                    | Ozone                                     | μg-m3                  |
| 12               | NOₓ                   | Oxydes d'azote                            | μg-m3                  |
| 19               | Pb                    | Dans les PM₁₀ plomb dans les PM₁₀         | μg-m3                  |
| 24               | PM₁₀                  | Particules de diamètre inférieur à 10 μm  | μg-m3                  |
| 39               | PM₂.₅                 | Particules de diamètre inférieur à 2,5 μm | μg-m3                  |
| 80               | As dans les PM₁₀      | Arsenic dans les PM₁₀                     | ng-m3                  |
| 82               | Cd dans les PM₁₀      | Cadmium dans les PM₁₀                     | ng-m3                  |
| 87               | Ni dans les PM₁₀      | Nickel dans les PM₁₀                      | ng-m3                  |
| P6               | BaP dans les PM₁₀     | Benzo[a]pyrène dans les PM₁₀              | ng-m3                  |
| V4               | C₆H₆                  | Benzène                                   | μg-m3                  |

## Types de données disponibles

| Identifiant | Libellé                         | Type Statistique | Codes polluants                                      | Noms polluants |
|-------------|---------------------------------|-----------------|-----------------------------------------------------|----------------|
| a1          | Moy. horaire                    |                 | 01 \| 02 \| 03 \| 04 \| 08 \| 12 \| 24 \| 39 \| I1 \| I... | SO2 \| NO \| NO2 \| CO \| O3 \| NOX as NO2 \| PM10 \|... |
| a2          | Moy. journalière                | dMean           | 01 \| 02 \| 03 \| 04 \| 08 \| 12 \| 24 \| 39 \| I1 \| I... | SO2 \| NO \| NO2 \| CO \| O3 \| NOX as NO2 \| PM10 \|... |
| a10         | Max. journalier moy. hor.       | dMean           | 01 \| 02 \| 03 \| 04 \| 08 \| 12 \| 24 \| 39 \| I1 \| I... | SO2 \| NO \| NO2 \| CO \| O3 \| NOX as NO2 \| PM10 \|... |
| a7          | Moy. annuelle                   | aMean           | 01 \| 02 \| 03 \| 04 \| 08 \| 12 \| 19 \| 24 \| 39 \| 8... | SO2 \| NO \| NO2 \| CO \| O3 \| NOX as NO2 \| Pb in ... |
| a5          | Moy. mensuelle                  | mMean           | 39 \| V4                                             | PM2.5 \| C6H6 |
| d1          | AEI                             | AEI             | 39                                                  | PM2.5 |
| e6          | Dép. - Moy. An. - 20 µg/m3      | aMean           | 01 \| 39                                             | SO2 \| PM2.5 |
| e8          | Dép. - Moy. An. - 25 µg/m3      | aMean           | 39                                                  | PM2.5 |
| e9          | Dép. - Moy. An. - 25 µg/m3 *    | aMean           | 39                                                  | PM2.5 |
| 02          | Données QH                      |                 | 01 \| 02 \| 03 \| 04 \| 08 \| 12 \| 24 \| 39 \| V4  | SO2 \| NO \| NO2 \| CO \| O3 \| NOX as NO2 \| PM10 \|... |

## Client

- Necessite `GEODAIR_API_KEY=api_key` dans le fichier `.env`.
    - Si le fichier `.env` n'est pas dans le répertoire courant, `GeodairClient(env_path="/chemin/vers/.env")`

- `get_measurements`
    - Pour obtenir les données d'une station précise, utiliser paramètre `station` avec un code de station

- `get_sampling_points`
    - passer le code d'une station avec le paramètre `code_station` pour connaitre ses points de prélèvement.

Les méthodes renvoient des DataFrames sans nettoyage, avec les valeurs CSV conservées sous forme de chaînes (codes avec zéros initiaux inclus).

Le client attend la génération des mesures en réessayant les réponses 412 et 404 temporaires après génération,
avec un nombre de tentatives borné (5 par défaut).

Un appel direct à `download_export(id)` conserve une erreur immédiate sur 404 par défaut.

Les erreurs HTTP et réseau sont propagées via `requests`, notamment `requests.HTTPError` et `requests.Timeout`.

Les options `timeout`, `poll_interval` et `max_download_attempts` règlent ces limites.

### Exemples

```python
from air_quality_prediction.geodair import GeodairClient

with GeodairClient() as client:
    stations = client.get_stations(departement="75")
    polluants = client.get_pollutants()
    types = client.get_data_types(codes_polluants="03")
    mesures = client.get_measurements(
        date_debut="23/11/2026 00:00",
        date_fin="24/11/2026 00:00",
        type_donnee="a1",  # Moyenne horaire ; codes disponibles avec get_data_types().
        polluant="03",  # NO₂
        departement="75",
    )
```

#### Enregistrer un CSV

```python
with GeodairClient() as client:
    chemin = client.download_measurements_csv(
        date_debut="18/11/2025 00:00",
        date_fin="20/11/2025 00:00",
        type_donnee="a1",
        polluant="03",
        departement="75",
        directory="../../data/raw/geodair",
        filename="no2_paris.csv",  # Facultatif
    )
```

- Cette méthode accepte les mêmes filtres que `get_measurements`, conserve les octets du CSV reçu et retourne un `Path` absolu.
- Le dossier est créé au besoin.
- Un fichier existant provoque `FileExistsError` et n'est pas écrasé.
- Les chemins relatifs partent du répertoire courant :
  - dans un notebook lancé depuis `notebooks/eda`, utiliser `directory="../../data/raw/geodair"`

#### Télécharger une longue période par morceaux

```python
with GeodairClient(
    poll_interval=5,
    max_download_attempts=30,
    min_request_interval=5,
    max_rate_limit_retries=3,
    rate_limit_backoff=30,
) as client:
    chemin = client.download_measurements_chunked_csv(
        date_debut="01/01/2015 00:00",
        date_fin="01/01/2026 00:00",
        type_donnee="a1",
        polluant="03",
        departement="75",
        chunk_days=31,
        directory="../../data/raw/geodair",
        filename="no2_paris_2015_2025.csv",
        # resume_from="../../data/raw/geodair/<ancien_dossier>_chunks"
    )
```

- Les intervalles sont contigus et chaque CSV brut reste dans un sous-dossier stable `*_chunks`.
- Une fois tous les téléchargements terminés, les lignes sont concaténées dans le CSV final, avec un seul en-tête, sans calcul ni déduplication.
- L'assemblage se fait en flux, sans charger toute la période en mémoire.
- Si un morceau échoue, les fichiers précédents sont conservés et le fichier final n'est pas créé.
- Avec `resume=True` (par défaut), relancer exactement le même appel réutilise les morceaux terminés et télécharge ceux qui manquent. Garder la date de départ initiale pour assembler toute la période.
- Le manifeste `request.json` empêche de reprendre avec des filtres, dates ou un découpage différents. Les fichiers sont publiés seulement une fois complètement écrits ; les `.part` ne sont jamais repris.
- Réduire `chunk_days` si un morceau dépasse encore le nombre de lignes autorisé.
- Le dossier par défaut est `data/raw/geodair`, relatif au répertoire courant.
- Un fichier final existant n'est jamais écrasé. Sans `filename`, le nom dépend des paramètres et reste identique pour faciliter la reprise.
- Toutes les requêtes d'une instance sont espacées d'au moins`min_request_interval` secondes après la réponse précédente.
- Sur 429, le client respecte `Retry-After` (secondes ou date HTTP), sinon attend 30, 60 puis 120 secondes
par défaut. 
  - Cette limite s'applique à chaque requête et est distincte des tentatives d'attente 404/412.


##### Pour afficher les morceaux réutilisés, les téléchargements et les pauses 429 :

```python
import logging
logging.basicConfig(level=logging.INFO)
```