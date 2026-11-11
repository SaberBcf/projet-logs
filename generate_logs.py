"""Script de génération du jeu de logs : un seul fichier texte.

Exemple : python generate_logs.py --size 10GB
"""

import argparse
import os
import random
import time
from collections.abc import Iterator

ONE_GB = 1024 * 1024 * 1024
UNITS = {"KB": 1024, "MB": 1024 * 1024, "GB": ONE_GB}

START = 1793491200  # 2026-11-01T00:00:00Z en secondes depuis 1970
LINES_PER_SECOND = 20

P_ATTACK = 1 / 4000  # une vague de force brute toutes les 4000 lignes
P_EMPTY = 0.002
P_BROKEN = 0.01
P_DIRTY = 0.03

CLIENTS = [f"10.0.{a}.{b}" for a in range(80) for b in range(1, 251)]
UNSTABLE_CLIENTS = CLIENTS[:2000]  # les 10 % de clients qui ont des erreurs
USERS = [f"user{n}" for n in range(5000)]
# chaque utilisateur se connecte en SSH depuis son propre poste
HOME_IPS = {user: CLIENTS[n] for n, user in enumerate(USERS)}
ATTACKERS = [f"198.51.100.{n}" for n in range(10, 50)]
SOURCES = ["api"] * 35 + ["nginx"] * 20 + ["sshd"] * 20
SOURCES = SOURCES + ["firewall"] * 20 + ["db"] * 5

API_PATHS = ["/api/orders", "/api/users", "/api/products", "/api/cart"]
API_CODES = [200] * 12 + [201, 204, 400, 401, 403, 404, 500, 503]
DB_EVENTS = [("INFO", "query executed")] * 16 + [
    ("WARNING", "slow query"),
    ("ERROR", "deadlock detected"),
    ("CRITICAL", "connection pool exhausted"),
]
PORTS = [22, 25, 53, 80, 443, 3306, 3389, 8080]
LEVEL_VARIANTS = {
    "INFO": ["info", "Info"],
    "WARNING": ["warn", "warning"],
    "ERROR": ["err", "error"],
    "CRITICAL": ["crit", "critical"],
}


def timestamp(line_number: int) -> str:
    """Horodatage ISO 8601 : 20 événements par seconde simulée."""
    seconds = START + line_number // LINES_PER_SECOND
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seconds))


def level_for_code(code: int) -> str:
    """Niveau de sévérité d'après un code HTTP."""
    if code >= 500:
        return "ERROR"
    if code >= 400:
        return "WARNING"
    return "INFO"


def make_event(ip: str) -> tuple[str, str, str, str]:
    """Renvoie (niveau, source, utilisateur, message) d'un événement."""
    source = random.choice(SOURCES)
    user = random.choice(USERS)
    if source == "api":
        code = random.choice(API_CODES)
        path = random.choice(API_PATHS)
        message = f'{{"event": "request", "path": "{path}", "code": {code}}}'
        return level_for_code(code), source, user, message
    if source == "nginx":
        code = random.choice([200, 200, 200, 304, 404, 500])
        return level_for_code(code), source, "-", f"GET /index.html {code}"
    if source == "sshd":
        if random.random() < 0.02:
            return "ERROR", source, user, "login failure"
        return "INFO", source, user, "login success"
    if source == "db":
        level, message = random.choice(DB_EVENTS)
        return level, source, "-", message
    port = random.choice(PORTS)
    protocol = "UDP" if port == 53 else "TCP"
    return "INFO", source, "-", f"{ip}:{port}/{protocol}"


def make_dirty(fields: list[str]) -> None:
    """Ajoute un défaut que le nettoyage doit corriger."""
    kind = random.choice(["espaces", "niveau", "source"])
    if kind == "espaces":
        fields[3] = f"  {fields[3]}  "
    elif kind == "niveau":
        fields[1] = random.choice(LEVEL_VARIANTS[fields[1]])
    else:
        fields[2] = fields[2].upper()


def make_broken(fields: list[str]) -> str:
    """Renvoie une ligne avec un seul défaut qui la fait rejeter."""
    kind = random.choice(["champs", "date", "niveau", "ip", "contenu"])
    if kind == "champs":
        return " | ".join(fields[:3]) + "\n"
    if kind == "date":
        fields[0] = fields[0][:5] + "13" + fields[0][7:]
    elif kind == "niveau":
        fields[1] = "DEBUGX"
    elif kind == "ip":
        fields[3] = "300" + fields[3][fields[3].index(".") :]
    elif fields[5].startswith("{"):
        fields[5] = fields[5][:20]
    elif fields[2] == "firewall":
        fields[5] = fields[3] + ":http/TCP"
    else:
        return "corrupted record\n"
    return " | ".join(fields) + "\n"


def bruteforce(line_number: int) -> Iterator[str]:
    """Produit une série d'échecs de connexion depuis une même IP."""
    ip = random.choice(ATTACKERS)
    user = random.choice(["root", "admin"] + USERS[:50])
    stamp = timestamp(line_number)
    for _ in range(random.randint(2, 12)):
        yield f"{stamp} | ERROR | sshd | {ip} | {user} | login failure\n"
    if random.random() < 0.3:
        yield f"{stamp} | INFO | sshd | {ip} | {user} | login success\n"


def generate_lines(seed: int) -> Iterator[str]:
    """Produit des lignes de log sans fin, dans l'ordre chronologique."""
    random.seed(seed)
    line_number = 0
    while True:
        line_number += 1
        if random.random() < P_ATTACK:
            yield from bruteforce(line_number)
            continue
        ip = random.choice(CLIENTS)
        level, source, user, message = make_event(ip)
        if source == "sshd":
            ip = HOME_IPS[user]
        elif level in ("ERROR", "CRITICAL"):
            ip = random.choice(UNSTABLE_CLIENTS)
        fields = [timestamp(line_number), level, source, ip, user, message]
        roll = random.random()
        if roll < P_EMPTY:
            yield "\n"
        elif roll < P_EMPTY + P_BROKEN:
            yield make_broken(fields)
        else:
            if roll < P_EMPTY + P_BROKEN + P_DIRTY:
                make_dirty(fields)
            yield " | ".join(fields) + "\n"


def write_logs(path: str, size: int, seed: int) -> int:
    """Écrit des lignes dans path jusqu'à size octets ; renvoie la taille."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    written = 0
    next_report = size // 10
    with open(path, "w", encoding="utf-8", newline="\n") as file:
        for line in generate_lines(seed):
            file.write(line)
            written += len(line)
            if written >= next_report:
                print(f"{written / size:.0%}")
                next_report += size // 10
            if written >= size:
                break
    return written


def parse_size(text: str) -> int | None:
    """Convertit '100MB' ou '10GB' en octets ; None si invalide."""
    value = text.strip().upper().replace(",", ".")
    for unit, factor in UNITS.items():
        if value.endswith(unit):
            try:
                return int(float(value[: -len(unit)]) * factor)
            except ValueError:
                return None
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Génère un fichier de logs.")
    parser.add_argument("--size", default="100MB", help="ex. 100MB, 10GB")
    parser.add_argument("--output", default="data/generated/logs.log")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    size = parse_size(args.size)
    if size is None:
        parser.error(f"taille invalide : {args.size} (ex. 100MB, 10GB)")

    start = time.time()
    written = write_logs(args.output, size, args.seed)
    elapsed = time.time() - start
    gigabytes = written / ONE_GB
    print(f"{gigabytes:.2f} Go écrits dans {args.output} en {elapsed:.0f} s")


if __name__ == "__main__":
    main()
