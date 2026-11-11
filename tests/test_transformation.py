"""Tests du module de transformation des logs."""

import unittest
from collections import defaultdict

from logengine.transformation import normalize, to_log


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

        self.assertEqual(autre["payload"], "service started")
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

        self.assertEqual(dict(rejected), {"json_invalide": 1})

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

        self.assertEqual(dict(rejected), {"port_invalide": 2})


class TestPoint4Normalisation(unittest.TestCase):

    def test_niveaux_et_alias(self) -> None:

        for initial, attendu in (
            ("  warn  ", "WARNING"),
            ("err", "ERROR"),
            ("Crit", "CRITICAL"),
            ("info", "INFO"),
        ):

            brut = to_log(
                ligne("service started", level=initial),
                defaultdict(int)
            )

            assert brut is not None

            self.assertEqual(
                normalize(brut)["level"],
                attendu
            )

    def test_source_et_utilisateur_en_minuscules(self) -> None:

        brut = to_log(
            ligne("slow response", user="  Carol  ").replace(
                " | api | ", " | NGINX | "
            ),
            defaultdict(int),
        )

        assert brut is not None

        propre = normalize(brut)

        self.assertEqual(propre["source"], "nginx")
        self.assertEqual(propre["user"], "carol")
        self.assertEqual(propre["payload"], "slow response")

        absent = to_log(
            ligne("service started", user="  -  "),
            defaultdict(int)
        )

        assert absent is not None

        self.assertIsNone(normalize(absent)["user"])

    def test_protocole_et_payload_connexion(self) -> None:

        brut = to_log(
            ligne("198.51.100.7:22/tcp"),
            defaultdict(int)
        )

        assert brut is not None

        propre = normalize(brut)

        self.assertEqual(
            brut["connection"],
            ("198.51.100.7", 22, "tcp")
        )

        self.assertEqual(
            propre["connection"],
            ("198.51.100.7", 22, "TCP")
        )

        self.assertEqual(
            propre["payload"],
            "198.51.100.7:22/TCP"
        )

    def test_json_copie_et_idempotence(self) -> None:

        brut = to_log(
            ligne('{"event": "login", "status": " success ", "code": 200}'),
            defaultdict(int)
        )

        assert brut is not None

        propre = normalize(brut)

        payload_brut = brut["payload"]
        payload_propre = propre["payload"]

        assert isinstance(payload_brut, dict)
        assert isinstance(payload_propre, dict)

        self.assertEqual(payload_propre["status"], "success")
        self.assertEqual(payload_propre["code"], 200)

        # Le dictionnaire initial ne doit pas être modifié.
        self.assertEqual(payload_brut["status"], " success ")

        # Les deux dictionnaires doivent être distincts.
        self.assertIsNot(payload_propre, payload_brut)

        # Normaliser deux fois doit donner le même résultat.
        self.assertEqual(normalize(propre), propre)


if __name__ == "__main__":
    unittest.main()