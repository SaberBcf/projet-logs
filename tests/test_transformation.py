"""Tests des modules d'ingestion et de transformation."""

import unittest
from collections import defaultdict

from logengine.analytics import init_state
from logengine.detection import detect_bruteforce
from logengine.ingestion import read_lines, read_sources
from logengine.transformation import normalize, prepare_logs, to_log
from tests.fixtures import SAMPLE_EXPECTED


def ligne(message: str, *, level: str = "INFO", user: str = "alice") -> str:
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
            echec["payload"], {"event": "login", "status": "failure"}
        )

        self.assertEqual(
            succes["payload"], {"event": "login", "status": "success"}
        )

        self.assertEqual(autre["payload"], "service started")
        self.assertEqual(dict(rejected), {})

    def test_objet_json_devenu_dictionnaire(self) -> None:
        rejected = defaultdict(int)

        log = to_log(ligne('{"event": "page_view", "code": 200}'), rejected)

        assert log is not None

        payload = log["payload"]
        assert isinstance(payload, dict)

        self.assertEqual(payload["code"], 200)
        self.assertEqual(dict(rejected), {})

    def test_json_invalide_rejete(self) -> None:
        rejected = defaultdict(int)

        self.assertIsNone(
            to_log(ligne('{"event": "login", "status":'), rejected)
        )

        self.assertEqual(dict(rejected), {"json_invalide": 1})

    def test_connexion_routee_en_tuple(self) -> None:
        rejected = defaultdict(int)

        log = to_log(ligne("198.51.100.7:22/TCP", user="-"), rejected)

        assert log is not None

        self.assertEqual(log["connection"], ("198.51.100.7", 22, "TCP"))

        self.assertEqual(log["ip"], "192.0.2.10")
        self.assertEqual(log["payload"], "198.51.100.7:22/TCP")
        self.assertIsNone(log["user"])

    def test_ports_invalides_rejetes(self) -> None:
        rejected = defaultdict(int)

        self.assertIsNone(to_log(ligne("203.0.113.5:http/TCP"), rejected))

        self.assertIsNone(to_log(ligne("203.0.113.5:65536/TCP"), rejected))

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
                ligne("service started", level=initial), defaultdict(int)
            )

            assert brut is not None

            self.assertEqual(normalize(brut)["level"], attendu)

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
            ligne("service started", user="  -  "), defaultdict(int)
        )

        assert absent is not None

        self.assertIsNone(normalize(absent)["user"])

    def test_protocole_et_payload_connexion(self) -> None:

        brut = to_log(ligne("198.51.100.7:22/tcp"), defaultdict(int))

        assert brut is not None

        propre = normalize(brut)

        self.assertEqual(brut["connection"], ("198.51.100.7", 22, "tcp"))

        self.assertEqual(propre["connection"], ("198.51.100.7", 22, "TCP"))

        self.assertEqual(propre["payload"], "198.51.100.7:22/TCP")

    def test_json_copie_et_idempotence(self) -> None:

        brut = to_log(
            ligne('{"event": "login", "status": " success ", "code": 200}'),
            defaultdict(int),
        )

        assert brut is not None

        propre = normalize(brut)

        payload_propre = propre["payload"]
        payload_brut = brut["payload"]

        assert isinstance(payload_propre, dict)
        assert isinstance(payload_brut, dict)

        self.assertEqual(payload_propre["status"], "success")
        self.assertEqual(payload_propre["code"], 200)
        self.assertEqual(payload_brut["status"], " success ")

        self.assertIsNot(payload_propre, payload_brut)

        self.assertEqual(normalize(propre), propre)


class TestPoint5Flux(unittest.TestCase):
    def test_echantillon_et_compteurs(self) -> None:
        rejected = defaultdict(int)

        logs = list(prepare_logs(read_lines("data/sample.log"), rejected))

        self.assertEqual(len(logs), SAMPLE_EXPECTED["valid"])

        self.assertEqual(dict(rejected), SAMPLE_EXPECTED["rejected"])

        self.assertTrue(any(log["level"] == "INFO" for log in logs))

        self.assertTrue(any(log["level"] == "WARNING" for log in logs))

    def test_flux_reste_paresseux(self) -> None:
        rejected = defaultdict(int)
        lues = []

        def source():
            for texte in (ligne("service started"), ligne("login success")):
                lues.append(texte)
                yield texte

        flux = prepare_logs(source(), rejected)

        self.assertEqual(lues, [])
        self.assertEqual(dict(rejected), {})

        premier = next(flux)

        self.assertEqual(premier["payload"], "service started")
        self.assertEqual(len(lues), 1)

        deuxieme = next(flux)
        payload = deuxieme["payload"]

        assert isinstance(payload, dict)

        self.assertEqual(payload["status"], "success")

    def test_plusieurs_sources_sans_liste_intermediaire(self) -> None:
        rejected = defaultdict(int)

        chemins = ("data/sample.log", "data/sample.log")

        total = sum(1 for _ in prepare_logs(read_sources(chemins), rejected))

        self.assertEqual(total, 2 * SAMPLE_EXPECTED["valid"])

        self.assertEqual(
            dict(rejected),
            {motif: 2 * n for motif, n in SAMPLE_EXPECTED["rejected"].items()},
        )

    def test_integration_detection(self) -> None:
        rejected = defaultdict(int)
        state = init_state()

        alertes_aux_positions = []

        for position, log in enumerate(
            prepare_logs(read_lines("data/sample.log"), rejected), start=1
        ):
            if detect_bruteforce(log, state=state, threshold=3):
                alertes_aux_positions.append(position)

        self.assertEqual(alertes_aux_positions, [5])


if __name__ == "__main__":
    unittest.main()
