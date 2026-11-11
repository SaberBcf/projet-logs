"""Mesure de la mémoire utilisée par la partie B (analytics + detection).

Les logs sont fabriqués à la volée par un générateur : aucune liste de
logs n'est créée, seule la mémoire de l'état d'analyse est mesurée.

Lancement, depuis la racine du projet :
    python -m scripts.measure_memory
    python -m scripts.measure_memory --logs 100000000 --ips 50 --users 20
"""

import argparse
import random
import time
import tracemalloc
from collections.abc import Iterator

from logengine.analytics import init_state, update_stats
from logengine.detection import detect_bruteforce
from logengine.models import Log

THRESHOLD = 3
SEED = 42


def make_ip(n: int) -> str:
    """Transforme un entier en adresse IPv4 unique (10.x.y.z)."""
    return f"10.{(n >> 16) & 255}.{(n >> 8) & 255}.{n & 255}"


def generate_logs(total: int, n_ips: int, n_users: int) -> Iterator[Log]:
    """Produit `total` logs un par un, avec n_ips IP et n_users utilisateurs."""
    rng = random.Random(SEED)
    for i in range(total):
        ip = make_ip(rng.randrange(n_ips))
        user = f"user{rng.randrange(n_users)}"
        roll = rng.random()
        if roll < 0.6:
            level, payload = "ERROR", {"event": "login", "status": "failure"}
        elif roll < 0.85:
            level, payload = "INFO", {"event": "login", "status": "success"}
        else:
            level, payload = "INFO", {"event": "page_view", "status": "ok"}
        yield {
            "timestamp": f"2026-11-05T14:30:{i % 60:02d}Z",
            "level": level,
            "source": "sshd",
            "ip": ip,
            "user": user,
            "payload": payload,
            "connection": (ip, 22, "TCP"),
        }


def measure(
    total: int, n_ips: int, n_users: int, progress: bool = False
) -> tuple[float, float, int, int, int]:
    """Traite les logs et renvoie le pic mémoire (Mo), la durée (s),
    le nombre d'alertes, d'IP distinctes et de couples (ip, user) suivis."""
    tracemalloc.start()
    start = time.perf_counter()

    state = init_state()
    alerts = 0
    step = max(total // 10, 1)
    for i, log in enumerate(generate_logs(total, n_ips, n_users), start=1):
        update_stats(log, state)
        alerts += len(detect_bruteforce(log, state=state, threshold=THRESHOLD))
        if progress and i % step == 0:
            _, peak = tracemalloc.get_traced_memory()
            elapsed = time.perf_counter() - start
            print(
                f"  {i:>13,} logs | pic {peak / 1_000_000:7.2f} Mo | {elapsed:7.1f} s"
            )

    duration = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    distinct_ips = len(state["active_ips"])
    couples = len(state["auth_history"])
    return peak / 1_000_000, duration, alerts, distinct_ips, couples


SCENARIOS: tuple[tuple[str, int, int, int], ...] = (
    # (description, nombre de logs, IP différentes, utilisateurs différents)
    ("Peu d'IP, 10 000 logs", 10_000, 50, 20),
    ("Peu d'IP, 100 000 logs", 100_000, 50, 20),
    ("Peu d'IP, 1 000 000 logs", 1_000_000, 50, 20),
    ("Beaucoup d'IP, 100 000 logs", 100_000, 100_000, 1_000),
    ("Beaucoup d'IP, 1 000 000 logs", 1_000_000, 1_000_000, 10_000),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--logs", type=int, help="nombre de logs (un seul test)")
    parser.add_argument("--ips", type=int, default=50, help="IP possibles")
    parser.add_argument("--users", type=int, default=20, help="utilisateurs")
    return parser.parse_args()


def run_single(total: int, n_ips: int, n_users: int) -> None:
    """Un seul test, avec affichage de la progression tous les 10 %."""
    print(f"Test unique : {total:,} logs, {n_ips:,} IP, {n_users:,} users")
    print("Mesure en cours (tracemalloc ralentit le programme)...\n")
    peak_mb, duration, alerts, ips, couples = measure(
        total, n_ips, n_users, progress=True
    )
    print(
        f"\nRésultat : pic {peak_mb:.2f} Mo en {duration:.1f} s"
        f" | {ips:,} IP vues | {couples:,} couples | {alerts:,} alertes"
    )


def main() -> None:
    args = parse_args()
    if args.logs is not None:
        if args.logs < 1 or args.ips < 1 or args.users < 1:
            raise SystemExit("--logs, --ips et --users doivent être >= 1.")
        run_single(args.logs, args.ips, args.users)
        return

    print("Mesure en cours (tracemalloc ralentit le programme)...\n")
    header = (
        f"{'Scénario':<32}{'Logs':>11}{'IP vues':>11}{'Couples':>11}"
        f"{'Pic mémoire':>14}{'Durée':>10}{'Alertes':>10}"
    )
    print(header)
    print("-" * len(header))
    for name, total, n_ips, n_users in SCENARIOS:
        peak_mb, duration, alerts, ips, couples = measure(total, n_ips, n_users)
        print(
            f"{name:<32}{total:>11,}{ips:>11,}{couples:>11,}"
            f"{peak_mb:>11.2f} Mo{duration:>8.1f} s{alerts:>10,}"
        )


if __name__ == "__main__":
    main()