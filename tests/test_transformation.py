"""Tests du module de transformation des logs."""

import unittest
from collections import defaultdict

from logengine.transformation import to_log


def ligne(message: str, *, level: str = "INFO", user: str = "alice") -> str:
    """Construit une ligne valide dont on fait varier le message."""
    return (
        f"2026-11-05T14:30:01Z | {level} | api | "
        f"192.0.2.10 | {user} | {message}"
    )


class TestPoint3Interpretation(unittest.TestCase):

    def test_login_et_texte_libre(self) -> None:
        rejected = defaultdict(int)

        echec = to_log(ligne("login failure"), rejected)
        succes = to_log(ligne("login success"), rejected)
        autre = to_log(ligne("service started"), rejected)

        assert echec is not None
        assert succes is not None
        assert autre is not None

        self.assertEqual(
            echec["payload"],
            {"event": "login", "status": "failure"}
        )

        self.assertEqual(
            succes["payload"],
            {"event": "login", "status": "success"}
        )

        self.assertEqual(
            autre["payload"],
            "service started"
        )

        self.assertEqual(dict(rejected), {})

    def test_objet_json_devenu_dictionnaire(self) -> None:
        rejected = defaultdict(int)

        log = to_log(
            ligne('{"event": "page_view", "code": 200}'),
            rejected
        )

        assert log is not None

        payload = log["payload"]

        assert isinstance(payload, dict)

        self.assertEqual(payload["code"], 200)
        self.assertEqual(dict(rejected), {})

    def test_json_invalide_rejete(self) -> None:
        rejected = defaultdict(int)

        self.assertIsNone(
            to_log(
                ligne('{"event": "login", "status":'),
                rejected
            )
        )

        self.assertEqual(
            dict(rejected),
            {"json_invalide": 1}
        )

    def test_connexion_routee_en_tuple(self) -> None:
        rejected = defaultdict(int)

        log = to_log(
            ligne("198.51.100.7:22/TCP", user="-"),
            rejected
        )

        assert log is not None

        self.assertEqual(
            log["connection"],
            ("198.51.100.7", 22, "TCP")
        )

        self.assertEqual(log["ip"], "192.0.2.10")
        self.assertEqual(log["payload"], "198.51.100.7:22/TCP")
        self.assertIsNone(log["user"])

    def test_ports_invalides_rejetes(self) -> None:
        rejected = defaultdict(int)

        self.assertIsNone(
            to_log(ligne("203.0.113.5:http/TCP"), rejected)
        )

        self.assertIsNone(
            to_log(ligne("203.0.113.5:65536/TCP"), rejected)
        )

        self.assertEqual(
            dict(rejected),
            {"port_invalide": 2}
        )


if __name__ == "__main__":
    unittest.main()