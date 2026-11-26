# Expérimentations

## Protocole d'évaluation commun

Ce protocole constitue un cadre à préciser avant les premiers essais. Aucun
résultat ni choix de modèle n'est consigné à ce stade.

Comparer une référence naïve (persistance ou saisonnalité, à préciser), une
approche utilisant l'historique de pollution, puis une variante ajoutant la météo.
Conserver les mêmes cibles, fenêtres, observations évaluées et budgets de réglage
pour isoler l'apport des variables météo.

| Paramètre à figer avant comparaison | Valeur |
| --- | --- |
| Polluants, stations, cible et unité | À compléter |
| Granularité, horizons et instant d'émission | À compléter |
| Version du dataset et variables | À compléter |
| Dates d'entraînement, validation et test | À compléter |
| Fenêtres, nombre de plis et éventuel intervalle de séparation | À compléter |
| Modèles, référence, hyperparamètres et budget de recherche | À compléter |
| Métrique principale et seuil de gain attendu | À compléter |

Évaluer séparément le scénario rétrospectif avec ERA5 et le scénario utilisant
des prévisions météo disponibles à l'émission. Ne pas interpréter leurs résultats
comme une même preuve de performance opérationnelle.

## Validation temporelle

Respecter l'ordre chronologique, sans découpage aléatoire. Utiliser des fenêtres
successives d'entraînement puis de validation ; préciser si l'entraînement est
croissant ou glissant. Réserver la période la plus récente au test final et ne
pas l'utiliser pour sélectionner les variables ou régler les modèles.

```mermaid
flowchart LR
    A[Passé : entraînement] --> B[Validation temporelle]
    B --> C[Choix figés]
    C --> D[Futur réservé : test final]
```

Définir les coupures selon les dates des cibles : aucune cible d'entraînement ne
doit empiéter sur la période évaluée. Dimensionner si nécessaire un intervalle
de séparation selon les horizons et les fenêtres utilisées. Pour des stations
multiples, appliquer les mêmes coupures temporelles ; un test sur des stations
non vues répondrait à une question distincte, à documenter séparément.

## Métriques

Mesures proposées à confirmer avant les essais : MAE pour l'erreur absolue moyenne
et RMSE pour rendre compte des erreurs élevées, exprimées dans l'unité de la cible.
Rapporter les scores par polluant, horizon et fenêtre, avec les effectifs évalués
et la règle d'agrégation entre stations. Éviter de mélanger des unités différentes.

Pour une métrique d'erreur, le gain relatif peut être calculé par
`(erreur de référence - erreur du modèle) / erreur de référence`, uniquement
si l'erreur de référence est non nulle. Rapporter aussi l'écart absolu et la
variabilité entre fenêtres. Une amélioration ponctuelle ne suffit pas à conclure
à un gain robuste ; méthode d'estimation de l'incertitude : à compléter.

## Prévention du data leakage

- À chaque émission, utiliser seulement les mesures et prévisions effectivement
  disponibles, en tenant compte de leur délai de publication et des révisions.
- Construire retards et fenêtres mobiles à partir du passé disponible ; exclure
  les fenêtres centrées et les interpolations utilisant des observations futures.
- Ajuster imputation, normalisation, sélection de variables et modèle sur le seul
  entraînement de chaque pli, puis appliquer ces traitements à la validation.
- Pour la météo, contrôler la date d'émission et de disponibilité en plus de la
  date de validité. Une réanalyse future ne constitue pas une prévision passée.
- Contrôler les doublons, les jointures et le chevauchement des cibles aux coupures.
- Garder le test final hors de toute décision de réglage et tracer chaque essai.

## Journal des expérimentations

Aucune expérience consignée pour le moment.

| Identifiant | Date | Hypothèse | Statut | Fiche |
| --- | --- | --- | --- | --- |

Copier le [template Experiment Record](templates/experiment-record.md) comme
section de cette page, sous un titre `EXP-001 — Titre à compléter`, puis ajouter
son ancre au journal. Renseigner le commit, le dataset, les paramètres et le
notebook ou script permettant de reproduire l'essai. Garder les sorties détaillées
dans les notebooks et reporter ici uniquement la synthèse, y compris les échecs.
