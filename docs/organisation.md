# Organisation

## Répartition

| Membre | Fichiers | Notions évaluées |
|---|---|---|
| A | `ingestion.py`, `transformation.py` | `yield`, `yield from`, dictionnaires, tuples, `filter` + `lambda`, `map`, `match-case` |
| B | `analytics.py`, `detection.py` | `set`, `frozenset`, opérations `\| & - ^`, `defaultdict`, `while` + `for` avec `break`, `continue`, `else` |
| C | `rules.py`, `audit.py`, `cli.py`, `main.py` | `*args`, `**kwargs`, fonctions passées en argument, `globals()`, `locals()` |
| Tous | `models.py`, `tests/fixtures.py`, `README.md`, rapport PDF | Typage, PEP8, exceptions |

Chacun écrit les tests de ses fichiers dans `tests/test_<fichier>.py`.

## Étapes

| Étape | Objectif | Terminée quand |
|---|---|---|
| 1. Démarrage | Chacun clone, crée son venv, lit le contrat | `python -m unittest` passe chez les trois |
| 2. Version minimale | A lit `data/auth.log` ; B compte sur `fake_logs()` ; C fait la CLI et le moteur avec une règle simple | `python main.py --files data/auth.log` affiche un résumé |
| 3. Notions complètes | Les trois formats, la détection, la liste noire, l'audit | Toutes les cases ci-dessous sont cochées |
| 4. Fiabilisation | Tests des cas limites, mesure mémoire (`tracemalloc`), Ruff sans erreur | Tests verts, mesures notées |
| 5. Rendu | Rapport PDF, README, vérification sur un clone neuf | Le correcteur peut tout relancer |

## Couverture du barème

- [ ] Générateur avec `yield` (A)
- [ ] Sous-générateur avec `yield from` sur plusieurs fichiers (A)
- [ ] Lignes parsées en dictionnaires, champs variés (A)
- [ ] Tuples pour les métadonnées `(ip, port, protocole)` (A)
- [ ] `filter` + `lambda`, et `filter(None, ...)` (A)
- [ ] `map` + normalisation avec f-strings (A)
- [ ] `match-case` sur chaîne, dictionnaire et tuple (A)
- [ ] IP en erreur dans un `set` (B)
- [ ] Liste noire en `frozenset`, opérations `|`, `&`, `-`, `^` (B)
- [ ] Comptages avec `defaultdict` (B)
- [ ] Force brute avec `while`, `for`, `break`, `continue`, `else` de boucle (B)
- [ ] `apply_security_rules(*args, **kwargs)` avec fonctions en argument (C)
- [ ] Audit avec `globals()` et `locals()`, export d'un rapport (C)
- [ ] `requirements.txt`, venv, séparation `.py` / rapport (tous)
- [ ] Typage, PEP8, gestion des exceptions (tous)

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

Ne jamais ajouter `.venv/`, `__pycache__/` ni de fichier généré.
