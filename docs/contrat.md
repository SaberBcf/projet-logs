# Contrat commun

Ce document fixe ce que chaque module reçoit et renvoie. Les types
correspondants sont définis dans `logengine/models.py` : toute modification
du contrat se fait dans les deux fichiers, après accord des trois membres.

## Formats des sources

Chaque format arrive sous une forme différente, ce qui alimente les trois
branches du `match-case` du module 2.

| Fichier | Forme brute produite par l'ingestion | Exemple |
|---|---|---|
| `.log` | `str` | `2026-11-05T14:30:01Z \| ERROR \| 192.0.2.10 \| alice \| login failure` |
| `.jsonl` | `dict` (un objet JSON par ligne) | `{"timestamp": "...", "level": "error", "ip": "...", "user": "carol", "payload": {...}, "port": 443, "protocol": "tcp"}` |
| `.csv` | `tuple` `(timestamp, ip, port, protocole)` | `("2026-11-05T14:40:01Z", "192.0.2.10", 22, "TCP")` |

Texte `.log` : champs séparés par ` | `, utilisateur absent noté `-`.

## Log normalisé

Sortie du module 2, entrée des modules 3 et 4. Un seul Log circule à la fois.

| Champ | Type | Convention |
|---|---|---|
| `timestamp` | `str` | Format ISO 8601 UTC, ex. `2026-11-05T14:30:01Z` |
| `level` | `str` | `INFO`, `WARNING`, `ERROR` ou `CRITICAL`, en majuscules |
| `ip` | `str` | Adresse IPv4 |
| `user` | `str \| None` | `None` si absent |
| `payload` | `dict \| str` | Connexion : `{"event": "login", "status": "failure"}` ou `"success"` ; sinon texte brut |
| `connection` | `tuple` | `(ip, port, protocole)` ; port et protocole à `None` si absents ; protocole en majuscules |

## Alerte

Renvoyée par chaque règle, toujours sous forme de liste (vide si rien).

```python
{
    "rule": "bruteforce",
    "ip": "192.0.2.10",
    "user": "alice",
    "timestamp": "2026-11-05T14:30:05Z",
    "message": "3 echecs consecutifs",
}
```

## Fonctions

| Responsable | Fonction | Entrée → sortie |
|---|---|---|
| A | `read_lines(path)` | chemin → lignes une par une (`yield`) |
| A | `read_records(path)` | chemin → enregistrements bruts selon l'extension |
| A | `read_sources(paths)` | chemins → tous les enregistrements, dans l'ordre (`yield from`) |
| A | `to_log(raw)` | enregistrement brut → `Log` ou `None` si invalide (`match-case`) |
| A | `normalize(log)` | `Log` → `Log` nettoyé |
| A | `prepare_logs(raws)` | enregistrements bruts → flux de `Log` valides (`map`, `filter`, `lambda`) |
| B | `init_state()` | → état neuf |
| B | `update_stats(log, state)` | met à jour l'état, renvoie `None` |
| B | `detect_bruteforce(log, *, state, threshold, **options)` | règle → liste d'alertes |
| B | `summarize(state, blacklist)` | → dictionnaire de résultats |
| C | `load_blacklist(path)` | fichier → `frozenset` d'IP |
| C | `check_blacklist(log, *, blacklist, **options)` | règle → liste d'alertes |
| C | `apply_security_rules(*args, **kwargs)` | règles + configuration → toutes les alertes du Log |
| C | `export_audit(global_ctx, local_ctx, path)` | contextes → fichier JSON |
| C | `parse_args(argv)` | arguments → options |

Le moteur appelle chaque règle avec `rule(**kwargs)` : une règle prend ce
dont elle a besoin et ignore le reste grâce à `**options`.

## Règles de conduite

- Une entrée invalide ne doit jamais arrêter le programme : `to_log` renvoie
  `None` et `filter(None, ...)` la retire. Un fichier introuvable, en
  revanche, arrête le programme avec un message clair.
- Le flux n'est jamais converti en liste (`list()`, `readlines()`, tri
  global interdits). Un générateur ne se parcourt qu'une fois.
- Les fichiers sont lus dans l'ordre donné, chacun déjà trié par date.
- Les événements `INFO` sont conservés : un succès de connexion remet la
  série d'échecs à zéro.
- Le code doit fonctionner avec Python 3.10 : Ruff et Pylance le vérifient
  grâce à `pyproject.toml`.

## Développer sans attendre les autres

`tests/fixtures.py` fournit `fake_logs()`, un flux de 8 Log dont les
résultats attendus sont dans `EXPECTED`. B et C développent et testent sur ce
flux ; `data/auth.log` contient le même scénario au format texte.
