"""Module 4 : audit des variables en mémoire (introspection)."""

from typing import Any


def export_audit(
    global_ctx: dict[str, Any], local_ctx: dict[str, Any], path: str
) -> None:
    """Exporte en JSON le nom, le type et un aperçu des variables.

    Ne doit jamais consommer un générateur ni exporter tous les logs.
    """
    raise NotImplementedError
