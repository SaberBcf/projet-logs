"""Tests du module 3 : compteurs, ensembles d'IP et résumé."""

import unittest
from copy import deepcopy

from logengine.analytics import init_state, summarize, update_stats
from tests.fixtures import BLACKLIST, EXPECTED, TEST_LOGS, fake_logs


class TestAnalytics(unittest.TestCase):
    def setUp(self) -> None:
        """Repart d'un état neuf avant chaque test."""
        self.state = init_state()
        for log in fake_logs():
            update_stats(log, self.state)
        self.summary = summarize(self.state, BLACKLIST)

    def test_counters(self) -> None:
        for key in ("total", "levels", "sources", "users"):
            with self.subTest(key=key):
                self.assertEqual(self.summary[key], EXPECTED[key])

    def test_ip_sets(self) -> None:
        for key in ("active_ips", "error_ips"):
            with self.subTest(key=key):
                self.assertEqual(self.summary[key], EXPECTED[key])

    def test_set_operations(self) -> None:
        keys = ("union", "intersection", "difference", "symmetric_difference")
        for key in keys:
            with self.subTest(key=key):
                self.assertEqual(self.summary[key], EXPECTED[key])

    def test_empty_state(self) -> None:
        summary = summarize(init_state(), BLACKLIST)
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["levels"], {})
        self.assertEqual(summary["active_ips"], set())
        self.assertEqual(summary["union"], set(BLACKLIST))

    def test_user_none_not_counted(self) -> None:
        state = init_state()
        log = deepcopy(TEST_LOGS[0])
        log["user"] = None
        update_stats(log, state)
        self.assertEqual(dict(state["users"]), {})
        self.assertEqual(state["total"], 1)

    def test_critical_is_an_error(self) -> None:
        state = init_state()
        log = deepcopy(TEST_LOGS[3])  # INFO à l'origine
        log["level"] = "CRITICAL"
        update_stats(log, state)
        self.assertIn(log["ip"], state["error_ips"])

    def test_warning_is_not_an_error(self) -> None:
        state = init_state()
        log = deepcopy(TEST_LOGS[0])
        log["level"] = "WARNING"
        update_stats(log, state)
        self.assertEqual(state["error_ips"], set())


if __name__ == "__main__":
    unittest.main()
