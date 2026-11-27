"""Lecture et diagnostic des exports horaires départementaux de Météo-France."""

from pathlib import Path
import re

import pandas as pd

METADATA = {"NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "AAAAMMJJHH"}
QUALITY_LABELS = {
    0: "protégée (validation définitive)",
    1: "validée",
    2: "douteuse, en cours de vérification",
    9: "filtrée (contrôles de premier niveau)",
}


def read_hourly_files(paths):
    """Conserve les colonnes brutes, ajoute date UTC et provenance, sans filtrage.

    Les identifiants et dates brutes restent des chaînes. Les champs vides sont
    manquants. Aucune conversion d'unité, imputation ou déduplication implicite.
    """
    frames, inventory = [], []
    for path in sorted(map(Path, paths)):
        frame = pd.read_csv(
            path, sep=";", compression="infer", low_memory=False,
            dtype={"NUM_POSTE": "string", "AAAAMMJJHH": "string"},
        )
        inventory.append({
            "fichier": path.name, "lignes": len(frame),
            "colonnes": len(frame.columns), "taille_Mo": path.stat().st_size / 1e6,
            "schema": tuple(frame.columns),
        })
        dates = pd.to_datetime(
            frame["AAAAMMJJHH"], format="%Y%m%d%H", utc=True, errors="coerce",
        )
        derived = pd.DataFrame({"date_utc": dates, "fichier_source": path.name})
        frames.append(pd.concat([frame, derived], axis=1))
    if not frames:
        raise FileNotFoundError("Aucun fichier horaire fourni.")
    return pd.concat(frames, ignore_index=True), pd.DataFrame(inventory)


def read_descriptions(path):
    """Le fichier officiel nommé .csv est en réalité une liste CHAMP : texte."""
    descriptions = {}
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^([A-Z][A-Z0-9_]*)\s*:\s*(.*)$", line)
        if match:
            descriptions[match[1]] = match[2]
    return descriptions


def column_profile(frame, descriptions):
    """Dictionnaire enrichi avec types, exemples, cardinalité et taux de vide."""
    rows = []
    for column in frame.columns:
        quality = column.startswith("Q") and column[1:] in frame.columns
        family = (
            "métadonnée" if column in METADATA else
            "dérivée" if column in {"date_utc", "fichier_source"} else
            "qualité" if quality else
            "statut" if column.startswith("STATUS_") else "paramètre"
        )
        description = descriptions.get(column, "À documenter")
        if quality:
            description = f"Code qualité de {column[1:]} (voir légende)"
        rows.append({
            "colonne": column, "famille": family, "description": description,
            "type": str(frame[column].dtype),
            "renseignées": int(frame[column].count()),
            "manquantes_pct": 100 * frame[column].isna().mean(),
            "valeurs_distinctes": frame[column].nunique(),
            "exemples": frame[column].dropna().unique()[:3].tolist(),
        })
    return pd.DataFrame(rows).set_index("colonne")


def station_coverage(frame):
    """Couverture entre première et dernière heure observées, par station.

    Le nombre d'heures attendues suppose une série horaire continue sur cet
    intervalle, sans prétendre connaître les dates réelles d'activité du poste.
    """
    result = frame.groupby("NUM_POSTE").agg(
        nom=("NOM_USUEL", "first"), debut=("date_utc", "min"),
        fin=("date_utc", "max"), lignes=("date_utc", "size"),
        heures_uniques=("date_utc", "nunique"),
    )
    result["heures_attendues"] = (
        (result["fin"] - result["debut"]) / pd.Timedelta(hours=1) + 1
    ).astype("Int64")
    result["heures_absentes"] = result["heures_attendues"] - result["heures_uniques"]
    result["couverture_pct"] = 100 * result["heures_uniques"] / result["heures_attendues"]
    return result.sort_values("lignes", ascending=False)
