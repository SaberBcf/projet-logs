"""Interface en ligne de commande."""

import argparse
import os


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Lit les options de la ligne de commande et les vérifie."""
    parser = argparse.ArgumentParser(
        description="Analyse de fichiers de logs de sécurité."
    )
    parser.add_argument(
        "--files", nargs="+", required=True, help="fichiers de logs à lire"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=3,
        help="échecs consécutifs avant une alerte de force brute",
    )
    parser.add_argument(
        "--blacklist",
        default="data/blacklist.txt",
        help="fichier contenant une IP par ligne",
    )
    parser.add_argument(
        "--audit", help="fichier JSON où exporter l'audit des variables"
    )
    parser.add_argument(
        "--max-alerts",
        type=int,
        default=20,
        help="nombre d'alertes affichées en détail",
    )
    args = parser.parse_args(argv)

    if args.threshold < 1:
        parser.error("--threshold doit être supérieur ou égal à 1")
    if args.max_alerts < 0:
        parser.error("--max-alerts ne peut pas être négatif")
    for path in args.files + [args.blacklist]:
        if not os.path.isfile(path):
            parser.error(f"fichier introuvable : {path}")
    return args
