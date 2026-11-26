# Sources de données

AirRoute s'appuie sur des données de pollution atmosphérique et des données météorologiques pour étudier la prédictibilité des concentrations de polluants à Paris.

## Geod'air — Pollution atmosphérique

- **Producteur :** LCSQA et réseau des AASQA, dont Airparif.
- **Accès :** API Geod'air avec clé d'authentification.
- **Documentation :** https://www.geodair.fr/api-ext/swagger
- **Données :** concentrations de NO₂, PM10, PM2.5 et O₃.
- **Granularité :** horaire pour les mesures étudiées.
- **Périmètre :** stations de mesure parisiennes.
- **Licence :** à vérifier.

Ces données constituent les séries temporelles cibles du projet.

**Limites :** couverture variable selon les stations et les polluants, données manquantes, mesures potentiellement invalides et représentativité géographique limitée.

## Open-Meteo — Historique météorologique

- **Source :** réanalyse ERA5, distribuée via Open-Meteo.
- **Accès :** Historical Weather API.
- **Documentation :** https://open-meteo.com/en/docs/historical-weather-api
- **Données envisagées :** température, vent, humidité, pression, précipitations et rayonnement solaire.
- **Granularité :** horaire.
- **Licence :** à vérifier selon les données et les conditions d'accès.

Ces données permettent d'étudier l'influence des conditions météorologiques sur les concentrations de polluants.

**Limites :** données issues d'une réanalyse météorologique et non de mesures locales directes, résolution spatiale limitée.

## Open-Meteo — Prévisions météorologiques

- **Accès :** Previous Runs API et Single Runs API.
- **Documentation :** https://open-meteo.com/en/docs/previous-runs-api
- **Données :** prévisions météorologiques historiques et futures.
- **Horizons étudiés :** J+1, J+3, J+7 et J+14, sous réserve de disponibilité.
- **Licence :** à vérifier selon les données et les conditions d'accès.

Ces données permettent d'évaluer les modèles dans des conditions proches de leur utilisation réelle.

**Limites :** incertitude croissante avec l'horizon de prévision, profondeur historique et disponibilité variables selon les modèles météorologiques.

## Gestion des données

Les données brutes sont conservées dans `data/raw/` et les données préparées dans `data/processed/`.

Les règles de nettoyage, les transformations et les analyses de qualité sont documentées dans les notebooks associés.