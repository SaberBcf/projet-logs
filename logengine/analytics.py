"""Module 3 : compteurs, ensembles d'IP et résumé final."""

from typing import Any

from logengine.models import Log, State


def init_state() -> State:
    """Crée un état neuf : compteurs, ensembles d'IP, suivi des séries."""
    raise NotImplementedError


def update_stats(log: Log, state: State) -> None:
    """Met à jour les compteurs (defaultdict) et les ensembles d'IP (set)."""
    raise NotImplementedError


def summarize(state: State, blacklist: frozenset[str]) -> dict[str, Any]:
    """Construit le résumé final, dont les opérations | & - ^."""
    raise NotImplementedError
