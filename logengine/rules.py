"""Module 4 : moteur de règles et règle de liste noire."""

from typing import Any

from logengine.models import Alert, Log, Rule


def load_blacklist(path: str) -> frozenset[str]:
    """Lit un fichier contenant une IP par ligne."""
    raise NotImplementedError


def check_blacklist(
    log: Log, *, blacklist: frozenset[str], **options: Any
) -> list[Alert]:
    """Règle : alerte quand l'IP du Log est dans la liste noire."""
    raise NotImplementedError


def apply_security_rules(*args: Rule, **kwargs: Any) -> list[Alert]:
    """Appelle chaque règle reçue dans args avec la configuration kwargs.

    Exemple :
        apply_security_rules(
            detect_bruteforce, check_blacklist,
            log=log, state=state, threshold=3, blacklist=blacklist,
        )
    """
    raise NotImplementedError
