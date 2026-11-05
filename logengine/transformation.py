"""Module 2 : routage, filtrage et normalisation des enregistrements."""

from collections.abc import Iterable, Iterator

from logengine.models import Log, RawRecord


def to_log(raw: RawRecord) -> Log | None:
    """Convertit un enregistrement brut en Log (match-case).

    Renvoie None si l'enregistrement est invalide.
    """
    raise NotImplementedError


def normalize(log: Log) -> Log:
    """Nettoie un Log : niveau en majuscules, espaces superflus retirés."""
    raise NotImplementedError


def prepare_logs(raws: Iterable[RawRecord]) -> Iterator[Log]:
    """Enchaîne map, filter(None, ...), filter avec lambda et normalize.

    Ne doit jamais transformer le flux en liste.
    """
    raise NotImplementedError
