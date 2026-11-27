# Sources de données

Ce projet s'appuie sur des données de pollution atmosphérique et des données météorologiques pour étudier la prédictibilité des concentrations de polluants à Paris.

## Geod'air — Données « temps réel » de mesure des concentrations de polluants atmosphériques réglementés 

- **Producteur :** [LCSQA et réseau des AASQA, dont Airparif.](https://www.data.gouv.fr/datasets/donnees-temps-reel-de-mesure-des-concentrations-de-polluants-atmospheriques-reglementes-1) 
- **Accès :** API Geod'air avec clé d'authentification (base nationale de données de qualité de l’air)
- **Documentation :** https://www.geodair.fr/api-ext/swagger
- **Données :** concentrations de NO₂ et PM2.5
- **Granularité :** Moyenne horaire
- **Périmètre :** Paris
- **Licence :** [Licence Ouverte / Open Licence version 2.0](https://www.data.gouv.fr/pages/legal/licences/etalab-2-0)

**Limites :** couverture variable selon les stations et les polluants, données manquantes, mesures potentiellement invalides et représentativité géographique limitée.

## Météo-France — Données climatologiques de base - horaires 

- **Producteur :** Météo-France
- **Accès :** par département et par lots de période au format `csv.gz`, [data.gouv.fr](https://www.data.gouv.fr/datasets/donnees-climatologiques-de-base-horaires)
- **Documentation :** [meteo-france](https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/621510657/Donn+es+climatologiques#%F0%9F%95%B0%EF%B8%8F-Donn%C3%A9es-horaires)
- **Données :** cf. ci-après et [Champs horaires](api/meteo_france_descriptif_champs.md)
- **Granularité :** Données horaire
- **Périmètre :** Paris
- **Licence :** [Licence Ouverte / Open Licence version 2.0](https://www.data.gouv.fr/pages/legal/licences/etalab-2-0)

**Limites :** couverture variable selon les stations et les polluants, données manquantes, mesures potentiellement invalides et représentativité géographique limitée.

??? info "Exemple de données"
    - Température sous abri instantanée (en °C et 1/10)
    - Température du point de rosée (en °C et 1/10)
    - Humidité relative (en %)
    - Quantité de précipitation tombée en 1 heure (en mm et 1/10)
    - Force du vent moyenné sur 10 mn, mesurée à 10 m (en m/s et 1/10)
    - Direction de la force du vent (en rose de 360)
    - Force maximale du vent instantané dans l’heure, mesurée à 10 m (en m/s et 1/10)
    - Pression mer, seulement pour les postes dont l’altitude est inférieure ou égale à 750 m (en hPa et 1/10)
    - Pression station (en hPa et 1/10)
    - Rayonnement global horaire en heure UTC (en J/cm2)
    - Insolation horaire en heure UTC (en mn)