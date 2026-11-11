"""Point d'entrée : lance le pipeline complet."""

import time
from collections import defaultdict
from typing import Any

from logengine.analytics import init_state, summarize, update_stats
from logengine.audit import export_audit
from logengine.cli import parse_args
from logengine.detection import detect_bruteforce
from logengine.ingestion import read_sources
from logengine.models import Rejected
from logengine.rules import (
    apply_security_rules,
    check_blacklist,
    load_blacklist,
)
from logengine.transformation import prepare_logs

PROGRESS_EVERY = 1000000  # un message tous les millions de logs


def show(key: str, value: Any) -> None:
    """Affiche une valeur du résumé sans inonder la console."""
    if isinstance(value, (set, frozenset)):
        examples = list(value)[:3]
        print(f"{key} : {len(value)} (ex. {examples})")
    elif isinstance(value, dict) and len(value) > 10:
        print(f"{key} : {len(value)} différents")
    else:
        print(f"{key} : {value}")


def main() -> None:
    args = parse_args()
    blacklist = load_blacklist(args.blacklist)
    state = init_state()
    rejected: Rejected = defaultdict(int)
    alert_counts: defaultdict[str, int] = defaultdict(int)
    shown = 0
    start = time.time()

    logs = prepare_logs(read_sources(args.files), rejected)
    for count, log in enumerate(logs, start=1):
        update_stats(log, state)
        alerts = apply_security_rules(
            detect_bruteforce,
            check_blacklist,
            log=log,
            state=state,
            threshold=args.threshold,
            blacklist=blacklist,
        )
        for alert in alerts:
            alert_counts[alert["rule"]] += 1
            if shown < args.max_alerts:
                shown += 1
                rule, when, text = (
                    alert["rule"],
                    alert["timestamp"],
                    alert["message"],
                )
                print(f"ALERTE [{rule}] {when} : {text}")
        if count % PROGRESS_EVERY == 0:
            elapsed = time.time() - start
            print(f"... {count} logs traités en {elapsed:.0f} s")

    print("\n=== Résumé ===")
    for key, value in summarize(state, blacklist).items():
        show(key, value)
    print(f"Lignes rejetées : {sum(rejected.values())}")
    for reason, number in rejected.items():
        print(f"  {reason} : {number}")
    print("Alertes :")
    for rule, number in alert_counts.items():
        print(f"  {rule} : {number}")
    print(f"Durée totale : {time.time() - start:.0f} s")

    if args.audit:
        export_audit(globals(), locals(), args.audit)


if __name__ == "__main__":
    main()
