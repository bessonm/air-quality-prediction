# ADR-001 — Utilisation des stations de fond

- **Date :** à compléter
- **Statut :** Proposed

## Contexte

Nous souhaitons prédire la pollution à l'échelle de Paris plutôt qu'à proximité d'un axe routier particulier.

## Options envisagées

- Utiliser une station de référence.
- Utiliser les stations de trafic.
- Utiliser la moyenne des stations de fond.

## Décision et justification

Utiliser la moyenne journalière des stations de fond pour chaque polluant afin d'obtenir un indicateur global de la pollution de fond à Paris.

## Conséquences

- Réduction de l'influence des particularités locales.
- Simplification de la modélisation.
- Perte des variations locales de pollution.
- Risque de biais lorsque les stations disponibles changent dans le temps.

## Références

`notebooks/eda/001-analyse_no2_pm25_2015_2026_paris.ipynb`