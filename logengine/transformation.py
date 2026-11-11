"""Module 2 : découpage, routage, filtrage et normalisation des lignes."""

import json
import re
from collections.abc import Iterable, Iterator
from datetime import datetime
from ipaddress import AddressValueError, IPv4Address
from typing import Any

from logengine.models import Log, Rejected

NIVEAUX_ACCEPTES = {
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "WARN",
    "ERR",
    "CRIT",
}

CONNEXION_RE = re.compile(r"([0-9.]+):([^/\s]+)/([A-Za-z]+)")

ALIASES_NIVEAUX = {
    "WARN": "WARNING",
    "ERR": "ERROR",
    "CRIT": "CRITICAL",
}


def to_log(line: str, rejected: Rejected) -> Log | None:
    """Validation et routage des messages."""

    champs = line.split(" | ", 5)

    if len(champs) != 6:
        rejected["champs_manquants"] += 1
        return None

    timestamp, level, source, ip, user, message = champs

    timestamp = timestamp.strip()

    try:
        datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        rejected["date_invalide"] += 1
        return None

    ip = ip.strip()

    try:
        IPv4Address(ip)
    except AddressValueError:
        rejected["ip_invalide"] += 1
        return None

    niveau_a_verifier = level.strip().upper()

    if niveau_a_verifier not in NIVEAUX_ACCEPTES:
        rejected["niveau_inconnu"] += 1
        return None

    message = message.strip()

    candidat: str | dict[str, Any] | tuple[str, int, str] = message

    if message.startswith("{"):
        try:
            candidat = json.loads(message)
        except json.JSONDecodeError:
            rejected["json_invalide"] += 1
            return None

    else:
        connexion_trouvee = CONNEXION_RE.fullmatch(message)

        if connexion_trouvee is not None:
            adresse, port_texte, protocole = connexion_trouvee.groups()

            try:
                port = int(port_texte)
            except ValueError:
                rejected["port_invalide"] += 1
                return None

            if not 0 <= port <= 65535:
                rejected["port_invalide"] += 1
                return None

            try:
                IPv4Address(adresse)
            except AddressValueError:
                rejected["ip_invalide"] += 1
                return None

            candidat = (adresse, port, protocole)

    connection = (ip, None, None)

    match candidat:
        case "login failure":
            payload = {
                "event": "login",
                "status": "failure",
            }

        case "login success":
            payload = {
                "event": "login",
                "status": "success",
            }

        case dict() as donnees:
            payload = donnees

        case (str(adresse), int(port), str(protocole)):
            connection = (adresse, port, protocole)
            payload = message

        case str() as texte:
            payload = texte

    return {
        "timestamp": timestamp,
        "level": level,
        "source": source,
        "ip": ip,
        "user": None if user == "-" else user,
        "payload": payload,
        "connection": connection,
    }


def normalize(log: Log) -> Log:
    """Normalisation sans modification du log original."""

    niveau = log["level"].strip().upper()
    niveau = ALIASES_NIVEAUX.get(niveau, niveau)

    utilisateur = log["user"]

    if utilisateur is not None:
        utilisateur = utilisateur.strip().lower()

        if utilisateur == "-":
            utilisateur = None

    adresse_connexion, port, protocole = log["connection"]

    adresse_connexion = adresse_connexion.strip()

    if protocole is not None:
        protocole = protocole.strip().upper()

    donnees = log["payload"]

    if isinstance(donnees, dict):
        payload = {
            cle: valeur.strip() if isinstance(valeur, str) else valeur
            for cle, valeur in donnees.items()
        }

    else:
        payload = donnees.strip()

        if port is not None and protocole is not None:
            payload = f"{adresse_connexion}:{port}/{protocole}"

    return {
        "timestamp": log["timestamp"].strip(),
        "level": niveau,
        "source": log["source"].strip().lower(),
        "ip": log["ip"].strip(),
        "user": utilisateur,
        "payload": payload,
        "connection": (adresse_connexion, port, protocole),
    }


def prepare_logs(lines: Iterable[str], rejected: Rejected) -> Iterator[Log]:
    """Préparation progressive des logs."""

    # Lignes vides
    lignes_non_vides = filter(lambda ligne: bool(ligne.strip()), lines)

    # Parsing
    logs_parses = map(lambda ligne: to_log(ligne, rejected), lignes_non_vides)

    # Rejets
    logs_valides = filter(None, logs_parses)

    # Normalisation
    return map(normalize, logs_valides)
