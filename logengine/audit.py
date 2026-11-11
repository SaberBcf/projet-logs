"""Module 4 : audit des variables en mémoire (introspection)."""

import json
import sys
from typing import Any

PREVIEW_LENGTH = 80


def describe_scope(scope: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Décrit chaque variable : type, taille en octets et aperçu court.

    Les noms internes (__name__, __file__...) sont ignorés. L'aperçu
    est coupé à 80 caractères, et un générateur n'est jamais parcouru :
    str() affiche seulement son nom.
    """
    report = {}
    for name, value in scope.items():
        if name.startswith("__"):
            continue
        report[name] = {
            "type": type(value).__name__,
            "taille_octets": sys.getsizeof(value),
            "apercu": str(value)[:PREVIEW_LENGTH],
        }
    return report


def export_audit(
    global_ctx: dict[str, Any], local_ctx: dict[str, Any], path: str
) -> None:
    """Exporte en JSON l'audit des portées globale et locale."""
    report = {
        "globales": describe_scope(global_ctx),
        "locales": describe_scope(local_ctx),
    }
    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
    print(
        f"Audit exporté dans {path} : {len(report['globales'])} variables "
        f"globales, {len(report['locales'])} locales"
    )
