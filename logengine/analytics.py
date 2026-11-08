"""Module 3 : compteurs, ensembles d'IP et résumé final."""

from collections import defaultdict, deque
from typing import Any

from logengine.models import Log, State

# Niveaux considérés comme des erreurs pour l'ensemble error_ips.
ERROR_LEVELS: frozenset[str] = frozenset({"ERROR", "CRITICAL"})


def init_state() -> State:
    """Crée un état neuf : compteurs, ensembles d'IP, suivi des séries."""
    return {
        # Nombre total de logs analysés.
        "total": 0,
        # Compteurs : une clé absente démarre automatiquement à 0.
        "levels": defaultdict(int),
        "sources": defaultdict(int),
        "users": defaultdict(int),
        # Ensembles : une même IP n'est stockée qu'une seule fois.
        "active_ips": set(),
        "error_ips": set(),
        # Utilisés par detection.py :
        # (ip, user) -> derniers statuts de connexion ("failure"/"success").
        "auth_history": defaultdict(deque),
        # Couples (ip, user) déjà signalés, pour une seule alerte par série.
        "alerted": set(),
    }


def update_stats(log: Log, state: State) -> None:
    """Met à jour les compteurs (defaultdict) et les ensembles d'IP (set)."""
    state["total"] += 1
    state["levels"][log["level"]] += 1
    state["sources"][log["source"]] += 1

    if log["user"] is not None:
        state["users"][log["user"]] += 1

    state["active_ips"].add(log["ip"])

    if log["level"] in ERROR_LEVELS:
        state["error_ips"].add(log["ip"])


def summarize(state: State, blacklist: frozenset[str]) -> dict[str, Any]:
    """Construit le résumé final, dont les opérations | & - ^."""
    active: set[str] = state["active_ips"]

    return {
        "total": state["total"],
        "levels": dict(state["levels"]),
        "sources": dict(state["sources"]),
        "users": dict(state["users"]),
        "active_ips": set(active),
        "error_ips": set(state["error_ips"]),
        # Toutes les IP connues (actives ou blacklistées).
        "union": active | blacklist,
        # IP actives ET blacklistées : les plus dangereuses.
        "intersection": active & blacklist,
        # IP actives qui ne sont pas blacklistées.
        "difference": active - blacklist,
        # IP présentes dans un seul des deux ensembles.
        "symmetric_difference": active ^ blacklist,
    }