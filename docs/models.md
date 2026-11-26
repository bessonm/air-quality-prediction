# Model Card — AirRoute

## Description

| Caractéristique | Valeur |
|---|---|
| Version | 1.0.0 |
| Algorithme | À compléter |
| Variable cible | À compléter |
| Granularité temporelle | À compléter |
| Périmètre géographique | À compléter |
| Horizons supportés | À compléter |

## Données d'entraînement

- Sources de données :
- Période d'entraînement :
- Variables explicatives :
- Fréquence de réentraînement :

## Performances

Évaluation sur une période de test chronologiquement postérieure à la période d'entraînement, avec les informations disponibles au moment de la prédiction.

| Horizon | MAE baseline | MAE modèle | RMSE modèle | Gain MAE |
|---|---:|---:|---:|---:|
| J+1 | — | — | — | — |
| J+3 | — | — | — | — |
| J+7 | — | — | — | — |
| J+14 | — | — | — | — |

Période de test : à compléter.

Les performances détaillées et le protocole d'évaluation sont disponibles dans les notebooks d'expérimentation.

## Usage prévu

Anticiper les concentrations de polluants atmosphériques afin de fournir une aide à la décision préventive.

## Limites

- Dépendance à la qualité des données de pollution et des prévisions météorologiques.
- Incertitude potentiellement croissante avec l'horizon de prédiction.
- Généralisation à d'autres stations ou territoires non démontrée.
- Capacité à anticiper les pics de pollution à évaluer.
- Absence de modélisation causale de l'impact des mesures de restriction du trafic.

Le modèle ne se substitue pas aux dispositifs officiels de surveillance et d'alerte.

## Références

- Notebook d'entraînement et d'évaluation.
- Version du dataset.
- Décision relative au choix du modèle.
- Version du code source.
