"""Module 1 : lecture progressive des fichiers de logs."""

from collections.abc import Iterable, Iterator


def read_lines(path: str) -> Iterator[str]:
    """Fournit les lignes du fichier sans le /n a la fin"""
    with open(path, "r", encoding="utf-8") as fichier:
        for ligne in fichier:
            yield ligne.rstrip("\n")


def read_sources(paths: Iterable[str]) -> Iterator[str]:
    """Fournit les lignes de plusieurs fichiers a la suite"""
    for path in paths:
        yield from read_lines(path)
