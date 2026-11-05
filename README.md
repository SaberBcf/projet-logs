# Moteur d'analyse de journaux

Outil en ligne de commande qui lit des journaux système et réseau au fil de
l'eau, les normalise, calcule des statistiques et signale les comportements
suspects : attaques par force brute et adresses IP en liste noire.

## Prérequis

Python 3.10 ou plus récent.

Le projet n'utilise que la bibliothèque standard : `requirements.txt`,
généré par `pip freeze`, est donc vide.

## Installation

Windows (PowerShell) :

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Linux / macOS :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Utilisation

```bash
python main.py --files data/auth.log data/app.jsonl data/network.csv --threshold 3 --blacklist data/blacklist.txt --audit audit.json
```

| Option | Rôle |
|---|---|
| `--files` | Un ou plusieurs fichiers, lus dans l'ordre donné |
| `--threshold` | Nombre d'échecs consécutifs qui déclenche une alerte |
| `--blacklist` | Fichier contenant une IP par ligne |
| `--audit` | Fichier JSON où exporter l'audit des variables |

## Tests

```bash
python -m unittest
```

## Structure

```
main.py                 point d'entrée
logengine/
    models.py           types partagés (Log, Alert, Rule)
    ingestion.py        module 1 : lecture progressive
    transformation.py   module 2 : routage, filtrage, normalisation
    analytics.py        module 3 : compteurs et ensembles
    detection.py        module 3 : force brute
    rules.py            module 4 : moteur de règles, liste noire
    audit.py            module 4 : introspection
    cli.py              options de la ligne de commande
tests/                  tests unitaires et jeu de test commun
data/                   fichiers de démonstration
docs/contrat.md         formats et signatures communs
```

## Équipe

| Membre | Partie |
|---|---|
| Yann DIARRASSOUBA | Ingestion et transformation (modules 1 et 2) |
| Dhanoush KESSAVANE | Analyse et détection (module 3) |
| Saber BOUCIOUF | Règles, audit, ligne de commande (module 4, `main.py`) |
