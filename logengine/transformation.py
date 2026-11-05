"""Module 2 : découpage, routage, filtrage et normalisation des lignes."""

from collections.abc import Iterable, Iterator

from logengine.models import Log, Rejected


def to_log(line: str, rejected: Rejected) -> Log | None:
    """Convertit une ligne en Log.

    Découpe les 6 champs, décode le message (chaîne, JSON ou connexion)
    et le route avec match-case. Si la ligne est invalide, incrémente
    rejected[motif] et renvoie None.
    """
    raise NotImplementedError


def normalize(log: Log) -> Log:
    """Nettoie un Log : majuscules, minuscules, espaces, alias de niveau."""
    raise NotImplementedError


def prepare_logs(lines: Iterable[str], rejected: Rejected) -> Iterator[Log]:
    """Enchaîne les étapes sans jamais transformer le flux en liste.

    filter avec lambda (lignes vides), map avec lambda (to_log),
    filter(None, ...) (lignes rejetées), map(normalize).
    """
    raise NotImplementedError
