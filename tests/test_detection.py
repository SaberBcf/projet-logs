"""Tests du module 3 : détection de force brute."""

import unittest
from copy import deepcopy

from logengine.analytics import init_state
from logengine.detection import detect_bruteforce
from logengine.models import Log
from tests.fixtures import EXPECTED, IP_A, IP_B, TEST_LOGS, THRESHOLD, fake_logs


def login(ip: str, user: str | None, status: str, n: int = 0) -> Log:
    """Fabrique un log de connexion pour les tests."""
    log = deepcopy(TEST_LOGS[0])
    log["ip"] = ip
    log["user"] = user
    log["timestamp"] = f"2026-11-05T15:00:{n:02d}Z"
    log["payload"] = {"event": "login", "status": status}
    return log


def run(logs: list[Log], threshold: int = THRESHOLD) -> list[int]:
    """Renvoie les numéros (à partir de 1) des logs qui ont alerté."""
    state = init_state()
    alerted_at = []
    for n, log in enumerate(logs, start=1):
        if detect_bruteforce(log, state=state, threshold=threshold):
            alerted_at.append(n)
    return alerted_at


class TestDetectBruteforce(unittest.TestCase):
    def test_reference_scenario(self) -> None:
        self.assertEqual(run(list(fake_logs())), EXPECTED["bruteforce_alerts_at"])

    def test_alert_content(self) -> None:
        state = init_state()
        alerts = []
        for log in fake_logs():
            alerts += detect_bruteforce(log, state=state, threshold=THRESHOLD)
        self.assertEqual(len(alerts), 1)
        alert = alerts[0]
        self.assertEqual(alert["rule"], "bruteforce")
        self.assertEqual(alert["ip"], IP_A)
        self.assertEqual(alert["user"], "alice")
        self.assertEqual(alert["timestamp"], TEST_LOGS[4]["timestamp"])

    def test_zero_failures(self) -> None:
        self.assertEqual(run([]), [])

    def test_below_threshold(self) -> None:
        logs = [login(IP_A, "alice", "failure") for _ in range(THRESHOLD - 1)]
        self.assertEqual(run(logs), [])

    def test_exactly_threshold(self) -> None:
        logs = [login(IP_A, "alice", "failure") for _ in range(THRESHOLD)]
        self.assertEqual(run(logs), [THRESHOLD])

    def test_above_threshold_single_alert(self) -> None:
        logs = [login(IP_A, "alice", "failure") for _ in range(THRESHOLD + 2)]
        self.assertEqual(run(logs), [THRESHOLD])

    def test_success_in_the_middle(self) -> None:
        logs = [
            login(IP_A, "alice", "failure"),
            login(IP_A, "alice", "failure"),
            login(IP_A, "alice", "success"),
            login(IP_A, "alice", "failure"),
            login(IP_A, "alice", "failure"),
        ]
        self.assertEqual(run(logs), [])

    def test_rearm_after_success(self) -> None:
        logs = [login(IP_A, "alice", "failure") for _ in range(3)]
        logs.append(login(IP_A, "alice", "success"))
        logs += [login(IP_A, "alice", "failure") for _ in range(3)]
        self.assertEqual(run(logs), [3, 7])

    def test_same_ip_two_users(self) -> None:
        logs = [
            login(IP_A, "alice", "failure"),
            login(IP_A, "bob", "failure"),
            login(IP_A, "alice", "failure"),
            login(IP_A, "bob", "failure"),
        ]
        self.assertEqual(run(logs), [])

    def test_interleaved_users(self) -> None:
        logs = []
        for _ in range(3):
            logs.append(login(IP_A, "alice", "failure"))
            logs.append(login(IP_B, "bob", "failure"))
        self.assertEqual(run(logs), [5, 6])

    def test_user_none_ignored(self) -> None:
        logs = [login(IP_A, None, "failure") for _ in range(5)]
        self.assertEqual(run(logs), [])

    def test_raw_string_payload_ignored(self) -> None:
        log = login(IP_A, "alice", "failure")
        log["payload"] = "login failure"
        self.assertEqual(run([log] * 5), [])

    def test_history_stays_bounded(self) -> None:
        state = init_state()
        for _ in range(100):
            log = login(IP_A, "alice", "failure")
            detect_bruteforce(log, state=state, threshold=THRESHOLD)
        self.assertEqual(len(state["auth_history"][(IP_A, "alice")]), THRESHOLD)

    def test_extra_options_accepted(self) -> None:
        state = init_state()
        log = login(IP_A, "alice", "failure")
        result = detect_bruteforce(
            log, state=state, threshold=THRESHOLD, blacklist=frozenset()
        )
        self.assertEqual(result, [])

    def test_invalid_threshold(self) -> None:
        with self.assertRaises(ValueError):
            detect_bruteforce(
                login(IP_A, "alice", "failure"), state=init_state(), threshold=0
            )


if __name__ == "__main__":
    unittest.main()