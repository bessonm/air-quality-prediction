# ADR-002 — Utilisation de la persistance comme référence

- **Date :** à compléter
- **Statut :** Proposed

## Contexte

Nous avons besoin d'une référence simple pour mesurer l'intérêt des modèles prédictifs.

## Options envisagées

- Persistance : demain = aujourd'hui.
- Prophet sans données météorologiques.

## Décision et justification

Retenir la persistance comme référence principale à J+1, car elle obtient de meilleurs résultats lors de la première expérimentation.

| Polluant | MAE Persistance | MAE Prophet |
|---|---:|---:|
| NO₂ | 5,71 | 6,25 |
| PM2.5 | 3,13 | 4,68 |

Erreurs exprimées en µg/m³.

## Conséquences

- Les prochains modèles devront être comparés à cette référence à protocole identique.
- Les performances restent à évaluer aux autres horizons.
- Prophet reste un modèle candidat.

## Références

`notebooks/eda/001-analyse_no2_pm25_2015_2026_paris.ipynb`