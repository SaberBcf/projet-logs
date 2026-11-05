"""Jeu de test commun : 8 événements dont les résultats sont connus."""

from collections.abc import Iterator
from copy import deepcopy

from logengine.models import Log

IP_A = "192.0.2.10"
IP_B = "192.0.2.20"
IP_C = "198.51.100.7"

BLACKLIST: frozenset[str] = frozenset({IP_B, IP_C})
THRESHOLD = 3


def _log(
    n: int, level: str, ip: str, user: str, event: str, status: str
) -> Log:
    return {
        "timestamp": f"2026-11-05T14:30:0{n}Z",
        "level": level,
        "ip": ip,
        "user": user,
        "payload": {"event": event, "status": status},
        "connection": (ip, 22, "TCP"),
    }


TEST_LOGS: tuple[Log, ...] = (
    _log(1, "ERROR", IP_A, "alice", "login", "failure"),
    _log(2, "ERROR", IP_B, "bob", "login", "failure"),
    _log(3, "ERROR", IP_A, "alice", "login", "failure"),
    _log(4, "INFO", IP_A, "alice", "page_view", "ok"),
    _log(5, "ERROR", IP_A, "alice", "login", "failure"),
    _log(6, "ERROR", IP_A, "alice", "login", "failure"),
    _log(7, "INFO", IP_A, "alice", "login", "success"),
    _log(8, "ERROR", IP_A, "alice", "login", "failure"),
)

# Résultats attendus avec THRESHOLD = 3 et BLACKLIST ci-dessus.
EXPECTED = {
    "total": 8,
    "levels": {"ERROR": 6, "INFO": 2},
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


def fake_logs() -> Iterator[Log]:
    """Fournit des copies neuves des logs de test, une par une."""
    for log in TEST_LOGS:
        yield deepcopy(log)
