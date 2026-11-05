"""Types partagés par tous les modules : le contrat commun en code."""

from collections import defaultdict
from collections.abc import Callable
from typing import Any, TypeAlias, TypedDict

LEVELS: tuple[str, ...] = ("INFO", "WARNING", "ERROR", "CRITICAL")

# Métadonnées fixes d'une connexion : (ip, port, protocole).
Connection: TypeAlias = tuple[str, int | None, str | None]

# Nombre de lignes rejetées, par motif (voir docs/contrat.md).
Rejected: TypeAlias = defaultdict[str, int]

# État d'analyse, défini en détail par le module 3.
State: TypeAlias = dict[str, Any]


class Log(TypedDict):
    """Événement normalisé, produit à partir d'une ligne du fichier."""

    timestamp: str
    level: str
    source: str
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
