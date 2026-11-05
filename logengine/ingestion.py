"""Module 1 : lecture progressive des sources de journaux."""

from collections.abc import Iterable, Iterator

from logengine.models import RawRecord


def read_lines(path: str) -> Iterator[str]:
    """Renvoie les lignes d'un fichier une par une (yield)."""
    raise NotImplementedError


def read_records(path: str) -> Iterator[RawRecord]:
    """Renvoie les enregistrements bruts d'un fichier selon son extension.

    .log -> str, .jsonl -> dict, .csv -> tuple.
    """
    raise NotImplementedError


def read_sources(paths: Iterable[str]) -> Iterator[RawRecord]:
    """Enchaîne plusieurs fichiers dans l'ordre fourni (yield from)."""
    raise NotImplementedError
