# Données

Cette page regroupe les Data Cards sous forme de sections. Pour une nouvelle
source, copier le [template](templates/data-card.md) ici. Les informations
non vérifiées restent à compléter ; une période demandée ne prouve pas une
couverture effective complète.

## Geod'air

### Provenance et licence

- Source : API Geod'air ; client dans `src/air_quality_prediction/geodair.py`.
- Références du dépôt : `CONTRIBUTING.md` pour l'utilisation du client,
  `apis/geodair/swagger.yaml` pour le contrat API et
  `notebooks/eda/geodair.ipynb` pour l'exploration.
- Fichiers : `data/raw/geodair/no2_paris_a1_01_2015_11_2026.csv` et
  `data/raw/geodair/pm25_paris_a1_01_2015_11_2026.csv` ; morceaux et paramètres
  conservés dans les répertoires `*_chunks` avec `request.json`.
- Date d'extraction, version ou empreinte : à compléter.
- Licence des données, attribution et conditions de redistribution : à vérifier
  et à compléter pour les exports utilisés. La licence du code ne les détermine pas.

### Schéma

Les CSV utilisent un séparateur `;`. L'en-tête de l'export NO₂ contient notamment :

| Champs | Rôle | Vérification à compléter |
| --- | --- | --- |
| `Date de début`, `Date de fin` | Intervalle de mesure | Fuseau, bornes, parsing |
| `code site`, `nom site`, `Latitude`, `Longitude` | Identification et localisation | Stabilité des sites |
| `Polluant`, `valeur`, `valeur brute`, `unité de mesure` | Concentration | Types numériques et unités par export |
| `code qualité`, `validité` | Indicateurs qualité | Signification et filtres retenus |
| `taux de saisie`, `couverture temporelle`, `couverture de données` | Complétude déclarée | Disponibilité et interprétation |
| `type d'implantation`, `type d'influence` | Contexte de mesure | Catégories retenues |

Schéma exhaustif, types et différences entre exports : à compléter.

### Couverture et qualité

Le manifeste NO₂ demande le département `75`, le type horaire `a1` et la période
du 01/01/2015 au 24/11/2026. La couverture effective par station et polluant,
les valeurs manquantes, doublons, invalidités et ruptures de série restent à mesurer.
Les filtres finaux de sélection des stations et observations sont à compléter.

### Transformations et limites

Le client conserve les CSV bruts par morceaux et les concatène avec un seul
en-tête, sans déduplication. Les conversions, filtres qualité, déduplications,
agrégations et règles d'imputation destinées à l'analyse sont à documenter avec
leur référence de code et les effectifs avant/après traitement.

Points à examiner : doublons aux frontières des morceaux, changements de stations,
représentativité spatiale et délai de disponibilité des mesures validées.

## ERA5

### Provenance et licence

Source prévue : réanalyse ERA5. Produit exact, fournisseur, URL, version, date
d'extraction, empreinte, licence et attribution : à compléter.

### Schéma et couverture

Variables, unités, coordonnées, grille, niveaux, pas temporel, fuseau, période
et emprise extraites : à compléter. Préciser la méthode d'association aux stations.

### Qualité et transformations

Complétude, valeurs manquantes et contrôles : à compléter. Documenter les
conversions d'unités, l'interpolation spatiale et l'alignement temporel effectués.

### Limites

Une réanalyse sert ici à étudier rétrospectivement l'apport météo. Sa disponibilité
à chaque date d'émission doit être vérifiée avant toute interprétation opérationnelle.
Résolution spatiale, décalage avec les mesures locales et autres limites : à compléter.

## Prévisions météorologiques Open-Meteo

### Provenance et licence

Source prévue : prévisions Open-Meteo. API, produit, modèle fournisseur, URL,
version, date d'extraction, licence et conditions d'utilisation : à compléter.

### Schéma et couverture

Documenter séparément la date d'émission, la date de validité, l'échéance, la
disponibilité réelle et les coordonnées. Variables, unités, fuseau, horizons,
période d'archive et résolution : à compléter.

### Qualité et transformations

Disponibilité des anciennes prévisions, changements de modèle, données manquantes,
conversion des unités et association aux stations : à compléter. Conserver la
version de prévision utilisée pour chaque date de validité.

### Limites

Vérifier que le produit retenu conserve les prévisions telles qu'elles étaient
disponibles à l'époque. Une archive d'observations ou une série reconstruite ne
remplace pas cette preuve. Sans archive adaptée, l'évaluation opérationnelle
historique restera à réaliser.

## Assemblage pour les expériences

Pour chaque dataset dérivé, consigner les sources et empreintes, la clé de
jointure, les fuseaux, les règles spatiales et temporelles, les filtres et les
effectifs obtenus. Ces choix sont à compléter avant les expériences ; les
[règles contre les fuites de données](experiments.md#prevention-du-data-leakage)
s'appliquent à toutes les transformations.
