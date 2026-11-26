# Contexte et problématique

Dans quelle mesure les concentrations de polluants de l'air sont-elles prévisibles à partir de leur
historique, et quel apport les données météorologiques ont-elles à cette prévision ?

# Objectifs

- Caractériser la couverture et la qualité des données disponibles
- Établir une référence fondée sur l'historique de pollution
- Mesurer l'apport de la météo
- Produire une conclusion traçable, y compris si aucun gain n'est observé

# Périmètre du MVP

L'étude porte sur Paris. Des extractions Geod'air de NO₂ et PM₂.₅ sont présentes dans le dépôt.
Le choix final des cibles, stations, périodes, granularités et horizons reste à compléter.
ERA5 et les prévisions Open-Meteo sont les sources météorologiques à étudier.

La généralisation à d'autres territoires et l'exploitation en production sont hors périmètre.
Le choix des modèles et la conception finale restent ouverts à expérimentation.

# Hypothèses scientifiques à tester

- L'historique de pollution contient un signal prédictif au-delà d'une référence naïve
- La météo apporte une information supplémentaire à cet historique
- Le gain éventuel varie selon le polluant et l'horizon de prévision
- Un gain obtenu avec une réanalyse météo ne garantit pas un gain avec des prévisions disponibles en conditions réelles