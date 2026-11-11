# Organisation

Rendu : mercredi 11 novembre, 23 h 59. Soutenance : jeudi 12 novembre, avec
lancement du traitement complet devant le jury.

## Répartition

| Membre | Fichiers | Notions évaluées |
|---|---|---|
| A | `ingestion.py`, `transformation.py` | `yield`, `yield from`, dictionnaires, tuples, `filter` + `lambda`, `filter(None, ...)`, `map`, `match-case` |
| B | `analytics.py`, `detection.py` | `set`, `frozenset`, opérations `\| & - ^`, `defaultdict`, `while` + `for` avec `break`, `continue`, `else` |
| C | `rules.py`, `audit.py`, `cli.py`, `main.py`, `generate_logs.py` | `*args`, `**kwargs`, fonctions passées en argument, `globals()`, `locals()` ; jeu de 10 à 15 Go |
| Tous | `models.py`, `tests/fixtures.py`, `README.md`, rapport PDF | Typage, PEP8, exceptions |

Chacun écrit les tests de ses fichiers dans `tests/test_<fichier>.py`.

## Planning

| Jour | Objectif | Terminé quand |
|---|---|---|
| Jeudi 5 | Démarrage : chacun clone, crée son venv, lit le contrat | `python -m unittest` passe chez les trois |
| Vendredi 6 | Version minimale ; générateur capable de produire 100 Mo | `python main.py --files data/sample.log` affiche un résumé |
| Samedi 7 et dimanche 8 | Toutes les notions ; traitement d'un fichier de 1 Go | Toutes les cases ci-dessous cochées, durée sur 1 Go notée |
| Lundi 9 et mardi 10 | Fichier final de 10 à 15 Go, traitement complet chronométré, mesure mémoire, tests, zéro alerte Ruff | Traitement complet réussi sur la machine de la soutenance |
| Mercredi 11 | Rapport PDF, README, vérification sur un clone neuf ; rendu visé à 20 h | Dépôt rendu |
| Jeudi 12 | Soutenance | Chacun sait expliquer tout le pipeline |

## Couverture du barème

- [x] Générateur avec `yield` (A)
- [x] Sous-générateur avec `yield from` sur plusieurs fichiers (A)
- [x] Lignes parsées en dictionnaires, champs variés (A)
- [x] Tuples pour les métadonnées `(ip, port, protocole)` (A)
- [x] `filter` + `lambda`, et `filter(None, ...)` (A)
- [x] `map` + normalisation avec f-strings (A)
- [x] `match-case` sur chaîne, dictionnaire et tuple (A)
- [x] IP en erreur dans un `set` (B)
- [x] Liste noire en `frozenset`, opérations `|`, `&`, `-`, `^` (B)
- [x] Comptages avec `defaultdict` (B)
- [x] Force brute avec `while`, `for`, `break`, `continue`, `else` de boucle (B)
- [x] `apply_security_rules(*args, **kwargs)` avec fonctions en argument (C)
- [x] Audit avec `globals()` et `locals()`, export d'un rapport (C)
- [x] Fichier unique de 10 à 15 Go, varié, avec lignes à nettoyer et malformées (C)
- [x] `requirements.txt`, venv, rapport PDF (tous)
- [x] Typage, PEP8, gestion des exceptions (tous)

## Routine Git

Chacun travaille sur sa propre branche, puis la fusionne par une Pull Request
relue par un autre membre.

```bash
git switch main
git pull
git switch -c c/moteur-regles
# ... modifications, puis :
git add .
git commit -m "Moteur de règles : appel des règles reçues"
git push -u origin c/moteur-regles
```

Ensuite, sur GitHub : **Compare & pull request**, relecture, **Merge**.
Retour sur `main` avec `git switch main` puis `git pull`.

Ne jamais ajouter `.venv/`, `__pycache__/`, `data/generated/` ni de fichier
généré.
