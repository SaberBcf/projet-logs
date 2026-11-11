"""Module 3 : détection des attaques par force brute."""

from typing import Any

from logengine.models import Alert, Log, State

RULE_NAME = "bruteforce"
AUTH_STATUSES: frozenset[str] = frozenset({"failure", "success"})


def _auth_status(log: Log) -> str | None:
    """Renvoie "failure" ou "success" pour un log de connexion, sinon None."""
    match log["payload"]:
        case {"event": "login", "status": str(status)} if (
            status in AUTH_STATUSES
        ):
            return status
        case _:
            return None


def detect_bruteforce(
    log: Log, *, state: State, threshold: int, **options: Any
) -> list[Alert]:
    """Règle : alerte au seuil d'échecs de connexion consécutifs.

    Les séries sont suivies par couple (ip, user). Un succès remet la
    série à zéro. Une seule alerte par série.
    """
    if threshold < 1:
        raise ValueError(f"Le seuil doit être >= 1 (reçu : {threshold}).")

    status = _auth_status(log)
    user = log["user"]

    # Événement neutre (pas une connexion) ou utilisateur inconnu : ignoré.
    if status is None or user is None:
        return []

    key = (log["ip"], user)
    history = state["auth_history"][key]
    history.append(status)

    # Un succès réarme la détection : une nouvelle série pourra alerter.
    if status == "success":
        state["alerted"].discard(key)

    # while : on garde que les `threshold` derniers statuts (mémoire bornée).
    while len(history) > threshold:
        history.popleft()

    # Pas assez de tentatives, ou alerte déjà émise pour cette série.
    if len(history) < threshold or key in state["alerted"]:
        return []

    # for : on vérifie que les `threshold` derniers statuts sont des échecs.
    for previous in history:
        if previous == "failure":
            continue  # échec : on passe au statut suivant
        break  # un succès dans la fenêtre : pas d'attaque
    else:
        # Atteint seulement si la boucle n'a jamais fait break :
        # le cycle de détection est complet, on lève l'alerte.
        state["alerted"].add(key)
        return [
            {
                "rule": RULE_NAME,
                "ip": log["ip"],
                "user": user,
                "timestamp": log["timestamp"],
                "message": (
                    f"{threshold} échecs de connexion consécutifs "
                    f"pour {user} depuis {log['ip']}"
                ),
            }
        ]

    return []
