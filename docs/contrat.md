# Contrat commun

Ce document fixe ce que chaque module reçoit et renvoie. Les types
correspondants sont définis dans `logengine/models.py` : toute modification
du contrat se fait dans les deux fichiers, après accord des trois membres.

## Format d'une ligne

Le jeu de données est un seul fichier texte, une ligne par événement :

```
horodatage | niveau | source | ip | utilisateur | message
```

| Champ | Exemple | Règle |
|---|---|---|
| horodatage | `2026-11-05T14:30:01Z` | ISO 8601, UTC |
| niveau | `ERROR` | `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| source | `sshd` | Service qui a produit la ligne : `sshd`, `api`, `firewall`, `nginx`, `db`... |
| ip | `192.0.2.10` | Adresse IPv4 source |
| utilisateur | `alice` | `-` si absent |
| message | voir ci-dessous | Dernier champ : il peut contenir ` \| ` |

Le découpage se fait avec `ligne.split(" | ", 5)` : le `5` garantit que le
message reste entier.

### Les trois formes du message

| Message | Exemple | Devient |
|---|---|---|
| Texte brut | `login failure` | `str` |
| Objet JSON | `{"event": "login", "status": "success", "code": 200}` | `dict` (`json.loads`) |
| Connexion | `198.51.100.7:22/TCP` | `tuple` `(ip, port, protocole)` |

Le `match-case` du module 2 route ces trois formes.

## Anomalies produites par le générateur

### À nettoyer : la ligne est gardée après normalisation

| Anomalie | Exemple | Résultat |
|---|---|---|
| Espaces en trop autour d'un champ | `\|  warn  \|` | espaces retirés |
| Niveau en minuscules ou abrégé | `warn`, `err`, `crit` | `WARNING`, `ERROR`, `CRITICAL` |
| Source ou utilisateur en majuscules | `NGINX`, `Carol` | `nginx`, `carol` |
| Protocole en minuscules | `:443/tcp` | `TCP` |
| Ligne vide ou faite d'espaces | | ignorée par `filter` avec `lambda`, non comptée |

### À rejeter : la ligne est écartée et comptée par motif

| Motif (clé de `rejected`) | Exemple |
|---|---|
| `champs_manquants` | moins de 6 champs, ligne illisible |
| `date_invalide` | `2026-13-45T99:00:00Z` |
| `niveau_inconnu` | `DEBUGX` |
| `ip_invalide` | `300.1.2.3` |
| `json_invalide` | `{"event": "login", "st` |
| `port_invalide` | `203.0.113.5:http/TCP`, port hors de 0 à 65535 |

`data/sample.log` contient un exemple de chaque cas ; les résultats attendus
sont dans `tests/fixtures.py` (`SAMPLE_EXPECTED`).

## Log normalisé

Sortie du module 2, entrée des modules 3 et 4. Un seul Log circule à la fois.

| Clé | Type | Convention |
|---|---|---|
| `timestamp` | `str` | Format ISO 8601 UTC |
| `level` | `str` | En majuscules |
| `source` | `str` | En minuscules |
| `ip` | `str` | Adresse IPv4 |
| `user` | `str \| None` | En minuscules, `None` si absent |
| `payload` | `dict \| str` | Connexion texte `login failure` ou `login success` convertie en `{"event": "login", "status": "failure"}` ; sinon le message tel quel |
| `connection` | `tuple` | `(ip, port, protocole)` pour un message de connexion, sinon `(ip, None, None)` |

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
| A | `read_lines(path)` | chemin → lignes sans saut de ligne, une par une (`yield`) |
| A | `read_sources(paths)` | chemins → toutes les lignes, dans l'ordre (`yield from`) |
| A | `to_log(line, rejected)` | ligne → `Log`, ou `None` si invalide (`match-case`) |
| A | `normalize(log)` | `Log` → `Log` nettoyé |
| A | `prepare_logs(lines, rejected)` | lignes → flux de `Log` valides (`filter`, `map`, `lambda`) |
| B | `init_state()` | → état neuf |
| B | `update_stats(log, state)` | met à jour l'état, renvoie `None` |
| B | `detect_bruteforce(log, *, state, threshold, **options)` | règle → liste d'alertes |
| B | `summarize(state, blacklist)` | → dictionnaire de résultats |
| C | `load_blacklist(path)` | fichier → `frozenset` d'IP |
| C | `check_blacklist(log, *, blacklist, **options)` | règle → liste d'alertes |
| C | `apply_security_rules(*args, **kwargs)` | règles + configuration → toutes les alertes du Log |
| C | `export_audit(global_ctx, local_ctx, path)` | contextes → fichier JSON |
| C | `parse_args(argv)` | arguments → options |
| C | `generate_logs.py` | taille, chemin, graine → fichier de logs |

`rejected` est un `defaultdict(int)` créé par `main.py` : `to_log` y ajoute
1 au motif de chaque ligne rejetée, et le résumé final l'affiche.

Le moteur appelle chaque règle avec `rule(**kwargs)` : une règle prend ce
dont elle a besoin et ignore le reste grâce à `**options`.

## Règles de conduite

- Une ligne invalide ne doit jamais arrêter le programme. Un fichier
  introuvable, en revanche, l'arrête avec un message clair.
- Le flux n'est jamais converti en liste (`list()`, `readlines()`, tri
  global interdits). Un générateur ne se parcourt qu'une fois.
- Les lignes du fichier sont dans l'ordre chronologique.
- Les événements `INFO` sont conservés : un succès de connexion remet la
  série d'échecs à zéro.
- Le générateur utilise une graine fixe : les trois membres obtiennent
  exactement le même fichier, donc les mêmes résultats.
- Les fichiers générés vont dans `data/generated/`, ignoré par Git.
- Le code doit fonctionner avec Python 3.10 : Ruff et Pylance le vérifient
  grâce à `pyproject.toml`.

## Développer sans attendre les autres

`tests/fixtures.py` fournit `fake_logs()`, un flux de 8 Log dont les
résultats attendus sont dans `EXPECTED` : ce sont les 8 premières lignes de
`data/sample.log`, déjà normalisées. B et C développent et testent sur ce
flux.
