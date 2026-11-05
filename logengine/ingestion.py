"""Module 1 : lecture progressive des fichiers de logs."""

from collections.abc import Iterable, Iterator


def read_lines(path: str) -> Iterator[str]:
    """Renvoie les lignes d'un fichier une par une, sans le saut de ligne."""
    raise NotImplementedError


def read_sources(paths: Iterable[str]) -> Iterator[str]:
    """Enchaîne les lignes de plusieurs fichiers, dans l'ordre (yield from)."""
    raise NotImplementedError
