# Sources de données

Ce projet s'appuie sur des données de pollution atmosphérique et des données météorologiques pour étudier la prédictibilité des concentrations de polluants à Paris.

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