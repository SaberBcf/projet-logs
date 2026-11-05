"""Interface en ligne de commande."""

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Lit les options --files, --threshold, --blacklist et --audit."""
    raise NotImplementedError
