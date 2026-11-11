import tempfile
import unittest
from pathlib import Path
from typing import Any

from logengine.models import Alert
from logengine.rules import (
    apply_security_rules,
    check_blacklist,
    load_blacklist,
)
from tests.fixtures import BLACKLIST, EXPECTED, fake_logs


class TestLoadBlacklist(unittest.TestCase):
    def test_ignores_comments_empty_and_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "blacklist.txt"
            path.write_text("# commentaire\n\n192.0.2.20\n300.1.2.3\n")
            self.assertEqual(load_blacklist(str(path)), {"192.0.2.20"})


class TestCheckBlacklist(unittest.TestCase):
    def test_alert_only_on_event_2(self) -> None:
        alerted = [
            number
            for number, log in enumerate(fake_logs(), start=1)
            if check_blacklist(log, blacklist=BLACKLIST)
        ]
        self.assertEqual(alerted, EXPECTED["blacklist_alerts_at"])


class TestApplySecurityRules(unittest.TestCase):
    def test_calls_every_rule_with_config(self) -> None:
        def rule_a(**kwargs: Any) -> list[Alert]:
            seuil = str(kwargs["threshold"])
            return [
                {
                    "rule": "a",
                    "ip": "192.0.2.1",
                    "user": None,
                    "timestamp": "",
                    "message": seuil,
                }
            ]

        def rule_b(**kwargs: Any) -> list[Alert]:
            return []

        alerts = apply_security_rules(rule_a, rule_b, threshold=5)
        self.assertEqual([a["message"] for a in alerts], ["5"])

    def test_no_rule_gives_no_alert(self) -> None:
        self.assertEqual(apply_security_rules(threshold=3), [])


if __name__ == "__main__":
    unittest.main()
