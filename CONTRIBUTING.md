# Documentation

La documentation du projet utilise [Zensical](https://zensical.org/).

La documentation est accessible à l'adresse : [bessonm.github.io/air-quality-prediction](https://bessonm.github.io/air-quality-prediction/).

Pour voir des exemples de syntaxes en markdown et Zensical:
- [toolbox](docs/toolbox.md)
- preview [http://localhost:8000/toolbox/](http://localhost:8000/toolbox/)

## Decision Records

Les Decision Records conservent le contexte, les alternatives et les conséquences des choix structurants : 
- périmètre
- sélection des données
- protocole ou modèle retenu

Créer un fichier dans le dossier décisions (ex. 001-selection-polluant.md) et suivre le [template](docs/templates/decision-record.md), puis ajouter un lien sur [l'index](docs/decisions/index.md)


Elle références les données utilisées, les reflexions sur les modèles, l'architecture du projet et l'utilisation des clients api implémentés.

## Pour lancer la documentation en local
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