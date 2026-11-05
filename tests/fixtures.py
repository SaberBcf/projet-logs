"""Jeu de test commun : 8 événements dont les résultats sont connus.

Ce sont les 8 premières lignes de data/sample.log, déjà normalisées.
"""

from collections.abc import Iterator
from copy import deepcopy
from typing import Any

from logengine.models import Log

IP_A = "192.0.2.10"
IP_B = "192.0.2.20"
IP_C = "198.51.100.7"

BLACKLIST: frozenset[str] = frozenset({IP_B, IP_C})
THRESHOLD = 3

LOGIN_FAILURE = {"event": "login", "status": "failure"}
LOGIN_SUCCESS = {"event": "login", "status": "success"}
PAGE_VIEW = {"event": "page_view", "status": "ok", "code": 200}


def _log(
    n: int, level: str, source: str, ip: str, user: str, payload: Any
) -> Log:
    return {
        "timestamp": f"2026-11-05T14:30:0{n}Z",
        "level": level,
        "source": source,
        "ip": ip,
        "user": user,
        "payload": dict(payload),
        "connection": (ip, None, None),
    }


TEST_LOGS: tuple[Log, ...] = (
    _log(1, "ERROR", "sshd", IP_A, "alice", LOGIN_FAILURE),
    _log(2, "ERROR", "sshd", IP_B, "bob", LOGIN_FAILURE),
    _log(3, "ERROR", "sshd", IP_A, "alice", LOGIN_FAILURE),
    _log(4, "INFO", "api", IP_A, "alice", PAGE_VIEW),
    _log(5, "ERROR", "sshd", IP_A, "alice", LOGIN_FAILURE),
    _log(6, "ERROR", "sshd", IP_A, "alice", LOGIN_FAILURE),
    _log(7, "INFO", "sshd", IP_A, "alice", LOGIN_SUCCESS),
    _log(8, "ERROR", "sshd", IP_A, "alice", LOGIN_FAILURE),
)

# Résultats attendus avec THRESHOLD = 3 et BLACKLIST ci-dessus.
EXPECTED = {
    "total": 8,
    "levels": {"ERROR": 6, "INFO": 2},
    "sources": {"sshd": 7, "api": 1},
    "users": {"alice": 7, "bob": 1},
    "active_ips": {IP_A, IP_B},
    "error_ips": {IP_A, IP_B},
    "union": {IP_A, IP_B, IP_C},
    "intersection": {IP_B},
    "difference": {IP_A},
    "symmetric_difference": {IP_A, IP_C},
    # Numéros des événements (1 à 8) qui doivent déclencher une alerte.
    "bruteforce_alerts_at": [5],
    "blacklist_alerts_at": [2],
}

# Résultat attendu de la lecture complète de data/sample.log.
SAMPLE_EXPECTED = {
    "lines": 20,
    "empty": 1,
    "valid": 12,
    "rejected": {
        "champs_manquants": 2,
        "date_invalide": 1,
        "ip_invalide": 1,
        "json_invalide": 1,
        "niveau_inconnu": 1,
        "port_invalide": 1,
    },
}


def fake_logs() -> Iterator[Log]:
    """Fournit des copies neuves des logs de test, une par une."""
    for log in TEST_LOGS:
        yield deepcopy(log)
