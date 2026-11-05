"""Point d'entrée : lance le pipeline complet."""

from collections import defaultdict

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


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    blacklist = load_blacklist(args.blacklist)
    state = init_state()
    rejected: Rejected = defaultdict(int)

    logs = prepare_logs(read_sources(args.files), rejected)
    for log in logs:
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
            print(f"ALERTE [{alert['rule']}] {alert['message']}")

    for key, value in summarize(state, blacklist).items():
        print(f"{key} : {value}")
    print(f"Lignes rejetées : {sum(rejected.values())}")
    for reason, count in sorted(rejected.items()):
        print(f"  {reason} : {count}")

    if args.audit:
        export_audit(globals(), locals(), args.audit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
