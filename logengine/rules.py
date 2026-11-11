"""Module 4 : moteur de règles et règle de liste noire."""

from ipaddress import AddressValueError, IPv4Address
from typing import Any

from logengine.models import Alert, Log, Rule


def load_blacklist(path: str) -> frozenset[str]:
    """Lit un fichier contenant une IP par ligne ; ignore vides et #."""
    addresses = set()
    with open(path, encoding="utf-8") as file:
        for number, line in enumerate(file, start=1):
            address = line.strip()
            if address == "" or address.startswith("#"):
                continue
            try:
                IPv4Address(address)
            except AddressValueError:
                print(f"Liste noire, ligne {number} ignorée : {address}")
                continue
            addresses.add(address)
    return frozenset(addresses)


def check_blacklist(
    log: Log, *, blacklist: frozenset[str], **options: Any
) -> list[Alert]:
    """Règle : alerte quand l'IP du Log est dans la liste noire."""
    if log["ip"] not in blacklist:
        return []
    alert: Alert = {
        "rule": "blacklist",
        "ip": log["ip"],
        "user": log["user"],
        "timestamp": log["timestamp"],
        "message": f"activité d'une IP en liste noire : {log['ip']}",
    }
    return [alert]


def apply_security_rules(*args: Rule, **kwargs: Any) -> list[Alert]:
    """Appelle chaque règle reçue dans args avec la configuration kwargs.

    Exemple :
        apply_security_rules(
            detect_bruteforce, check_blacklist,
            log=log, state=state, threshold=3, blacklist=blacklist,
        )
    """
    alerts: list[Alert] = []
    for rule in args:
        alerts = alerts + rule(**kwargs)
    return alerts
