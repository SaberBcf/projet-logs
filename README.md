# Moteur d'analyse de journaux

Outil en ligne de commande qui lit un très gros fichier de logs système et
réseau au fil de l'eau, le nettoie, calcule des statistiques et signale les
comportements suspects : attaques par force brute et adresses IP en liste
noire.

## Prérequis

Python 3.10 ou plus récent, et 15 Go d'espace disque libre pour le jeu de
données.

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

## Générer le jeu de données

```bash
python generate_logs.py --size 15GB --output data/generated/logs.log --seed 42
```

Avec la même graine (`--seed`), le fichier produit est toujours identique.
Pour développer, une taille de `100MB` suffit.

## Lancer l'analyse

```bash
python main.py --files data/generated/logs.log --threshold 3 --blacklist data/blacklist.txt --audit audit.json
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
generate_logs.py        générateur du jeu de données
logengine/
    models.py           types partagés (Log, Alert, Rule)
    ingestion.py        module 1 : lecture progressive
    transformation.py   module 2 : découpage, routage, nettoyage
    analytics.py        module 3 : compteurs et ensembles
    detection.py        module 3 : force brute
    rules.py            module 4 : moteur de règles, liste noire
    audit.py            module 4 : introspection
    cli.py              options de la ligne de commande
tests/                  tests unitaires et jeu de test commun
data/                   exemple de logs et liste noire
docs/contrat.md         format des lignes, anomalies, signatures
```

## Équipe

| Membre | Partie |
|---|---|
| Yann DIARRASSOUBA | Ingestion et transformation (modules 1 et 2) |
| Dhanoush KESSAVANE | Analyse et détection (module 3) |
| Saber BOUCIOUF | Règles, audit, ligne de commande, script de génération (module 4, `main.py`, `generate_logs.py`) |
