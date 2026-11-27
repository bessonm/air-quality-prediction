# ADR-001 — Utilisation des stations de fond

- **Date :** 26/11/2026
- **Statut :** Accepted

## Contexte

Nous souhaitons prédire la pollution à l'échelle de Paris plutôt qu'à proximité d'un axe routier particulier.
Dans les données extraites, il y a des stations dites de "fond", dans la ville, et des stations "traffic" aux abords du boulevard périphérique.

## Options envisagées

- Soit utiliser une seule station de référence
- Soit utiliser uniquement les stations de trafic
- Soit utiliser la moyenne des stations de fond

## Décision et justification

Nous avons décidé dans un premier temps d'utiliser la moyenne journalière plutot que les moyennes horaires de nos données brutes.

Nous avons décidé d'utiliser les mesures des stations de fond plutot que celle du traffic pour être plus proche de la réalité d'une personne qui vit dans Paris.

Au vu de la disparité des mesures entre les polluants NO2 et PM2.5, nous avons différencié l'approche pour chaque polluant.

!!! note "NO2" 
    Prise de la moyenne des stations de fond (7e, 12e, 13e et 18e arrondissements)

!!! note "PM2.5"
    - De janvier 2015 à sept 2019: uniquement les mesures de la station `Paris Centre`
    - De octobre 2019 à 2022 : uniquement les mesures de la station `Les Halles`
    - De 2022 à 2024 : la moyenne des mesures des stations `Les Halles` et `18e`


## Conséquences

- Réduction de l'influence des particularités locales en ne prennant pas en compte les mesures proches axe routier périphérique
- Cela simplifie la modélisation.
- Perte des variations locales de pollution.
- On a un risque de biais lorsque les stations disponibles changent dans le temps comme c'est le cas pour le PM2.5

## Références

[notebooks/eda/001-analyse_no2_pm25_2015_2026_paris.ipynb](https://github.com/bessonm/air-quality-prediction/blob/main/notebooks/eda/001-analyse_no2_pm25_2015_2026_paris.ipynb)