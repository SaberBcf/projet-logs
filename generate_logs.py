"""Générateur du jeu de logs : un seul fichier texte de 10 à 15 Go."""

from collections.abc import Iterator


def generate_lines(seed: int) -> Iterator[str]:
    """Produit des lignes de log sans fin (yield).

    Mélange les trois formes de message, injecte des scénarios
    (force brute, IP en liste noire) et une part de lignes à nettoyer
    ou malformées, décrites dans docs/contrat.md.
    """
    raise NotImplementedError


def write_logs(path: str, size_bytes: int, seed: int) -> None:
    """Écrit des lignes dans path jusqu'à atteindre size_bytes."""
    raise NotImplementedError


def parse_size(text: str) -> int:
    """Convertit une taille comme '100MB' ou '15GB' en octets."""
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Lit les options --size, --output et --seed, puis écrit le fichier."""
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
