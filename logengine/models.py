"""Types partagés par tous les modules : le contrat commun en code."""

from collections.abc import Callable
from typing import Any, TypeAlias, TypedDict

LEVELS: tuple[str, ...] = ("INFO", "WARNING", "ERROR", "CRITICAL")

# Métadonnées fixes d'une connexion : (ip, port, protocole).
Connection: TypeAlias = tuple[str, int | None, str | None]

# Formes brutes produites par l'ingestion, avant routage
# (exemples complets dans docs/contrat.md) :
#   .log   -> str
#   .jsonl -> dict
#   .csv   -> tuple (timestamp, ip, port, protocole)
RawRecord: TypeAlias = str | dict[str, Any] | tuple[str, str, int, str]

# État d'analyse, défini en détail par le module 3.
State: TypeAlias = dict[str, Any]


class Log(TypedDict):
    """Événement normalisé, identique quelle que soit la source."""

    timestamp: str
    level: str
    ip: str
    user: str | None
    payload: dict[str, Any] | str
    connection: Connection


class Alert(TypedDict):
    """Alerte renvoyée par une règle de sécurité."""

    rule: str
    ip: str
    user: str | None
    timestamp: str
    message: str


# Une règle reçoit un Log et la configuration, et renvoie ses alertes.
Rule: TypeAlias = Callable[..., list[Alert]]
