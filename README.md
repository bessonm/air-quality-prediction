# Air quality prediction project

This project aims to evaluate if and how weather forecasts can help improve the prediction of air pollution compared to using only historical pollution data.

| Dossier | Responsabilité |
|--------|--------|
| `app/` | Application Streamlit pour présenter les résultats |
| `data/` | Données extraites |
| `docs/` | Documentation technique du projet|
| `notebooks/` | Explorer, expérimenter, comprendre et valider des hypothèses |
| `src/` | Classes et fonctions réutilisables (ex. client api geod'air)|

## Contexte

Pour comprendre la pollution de l'air et ses impacts : https://www.ecologie.gouv.fr/politiques-publiques/polluants-lair-situation-impacts-encadrement

Pour comprendre la réglementation: https://www.geodair.fr/reglementation

## Documentation

La documentation du projet utilise [Zensical](https://zensical.org/).

Elle références les données utilisées, les reflexions sur les modèles, l'architecture du projet et l'utilisation des clients api implémentés.

### Pour lancer la documentation en local 
- Installer les dépendances : 
```bash
uv sync --locked --group dev
 ```

- Puis démarrer en local :
```bash
uv run --locked zensical serve
```

### Pour générer le site statique dans dossier `site/`
```bash 
uv run --locked zensical build --strict
```
