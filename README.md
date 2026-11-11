# Moteur d'analyse de journaux

Outil en ligne de commande qui lit un très gros fichier de logs système et
réseau au fil de l'eau, le nettoie, calcule des statistiques et signale les
comportements suspects : attaques par force brute et adresses IP en liste
noire.

## Prérequis

Python 3.10 ou plus récent (projet développé et mesuré avec Python 3.14),
et 15 Go d'espace disque libre pour le jeu de données.

Le projet n'utilise que la bibliothèque standard : `requirements.txt`,
généré par `pip freeze`, ne contient donc qu'une ligne de commentaire.

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

## Démonstration rapide

```bash
python main.py
```

Sans option, le programme exécute tout le pipeline sur l'échantillon fourni
`data/sample.log` (20 lignes) : 12 logs valides, 7 lignes rejetées et 3
alertes.

## Générer le jeu de données

```bash
python generate_logs.py --size 10GB --output data/generated/logs.log --seed 42
```

Avec la même graine (`--seed`), le fichier produit est toujours identique.
Pour développer, une taille de `100MB` suffit.

## Lancer l'analyse

```bash
python main.py --files data/generated/logs.log --audit audit.json
```

Sur le fichier de 10 Go (environ 118 millions de logs), le traitement dure
environ 19 minutes et le processus reste autour de 26 Mo de mémoire.

| Option | Rôle | Défaut |
|---|---|---|
| `--files` | Un ou plusieurs fichiers, lus dans l'ordre donné | `data/sample.log` |
| `--threshold` | Nombre d'échecs consécutifs qui déclenche une alerte | 3 |
| `--blacklist` | Fichier contenant une IP par ligne | `data/blacklist.txt` |
| `--audit` | Fichier JSON où exporter l'audit des variables | aucun |
| `--max-alerts` | Nombre d'alertes affichées en détail pendant le traitement | 20 |

## Tests

```bash
python -m unittest
```

Mesure de la mémoire du module 3 avec `tracemalloc` :

```bash
python -m scripts.measure_memory
```

## Structure

```
main.py                 point d'entrée
generate_logs.py        script de génération du jeu de données
logengine/
    models.py           types partagés (Log, Alert, Rule)
    ingestion.py        module 1 : lecture progressive
    transformation.py   module 2 : découpage, routage, nettoyage
    analytics.py        module 3 : compteurs et ensembles
    detection.py        module 3 : force brute
    rules.py            module 4 : moteur de règles, liste noire
    audit.py            module 4 : introspection
    cli.py              options de la ligne de commande
scripts/
    measure_memory.py   mesure de la mémoire du module 3
tests/                  tests unitaires et jeu de test commun
data/                   exemple de logs et liste noire
docs/
    contrat.md          format des lignes, anomalies, signatures
    organisation.md     répartition, planning, routine Git
    Rapport.pdf         rapport final
```

## Équipe

| Membre | Partie |
|---|---|
| Yann DIARRASSOUBA | Ingestion et transformation (modules 1 et 2) |
| Dhanoush KESSAVANE | Analyse et détection (module 3) |
| Saber BOUCIOUF | Règles, audit, ligne de commande, script de génération (module 4, `main.py`, `generate_logs.py`) |
