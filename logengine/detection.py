"""Module 3 : détection des attaques par force brute."""

from typing import Any

from logengine.models import Alert, Log, State


def detect_bruteforce(
    log: Log, *, state: State, threshold: int, **options: Any
) -> list[Alert]:
    """Règle : alerte au seuil d'échecs de connexion consécutifs.

    Les séries sont suivies par couple (ip, user). Un succès remet la
    série à zéro. Une seule alerte par série.
    """
    raise NotImplementedError
