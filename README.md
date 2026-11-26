# Air quality prediction project

This project aims to evaluate if and how weather forecasts can help improve the prediction of air pollution compared to using only historical pollution data.

| Dossier | Responsabilité |
|--------|--------|
| `app/` | Application Streamlit pour présenter les résultats |
| `data/` | Données extraites |
| `docs/` | Documentation et suivi des décisions |
| `notebooks/` | Explorer, expérimenter, comprendre et valider des hypothèses |
| `src/` | Classes et fonctions réutilisables (ex. client api geod'air)|

## Documentation

La documentation du projet utilise [Zensical](https://zensical.org/).

Elle présente des explications sur la pollution de l'air et les polluants, les données utilisées, les expérimentations et les décisions.

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
