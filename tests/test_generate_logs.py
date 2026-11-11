import unittest

from generate_logs import (
    ATTACKERS,
    HOME_IPS,
    ONE_GB,
    UNSTABLE_CLIENTS,
    generate_lines,
    parse_size,
)


def first_lines(seed: int, count: int) -> list[str]:
    """Renvoie les premières lignes produites avec cette graine."""
    lines = []
    for line in generate_lines(seed):
        lines.append(line)
        if len(lines) == count:
            break
    return lines


class TestParseSize(unittest.TestCase):
    def test_units(self) -> None:
        self.assertEqual(parse_size("100MB"), 100 * 1024 * 1024)
        self.assertEqual(parse_size("10GB"), 10 * ONE_GB)
        self.assertEqual(parse_size("10,5 gb"), int(10.5 * ONE_GB))

    def test_invalid(self) -> None:
        self.assertIsNone(parse_size("dix gigas"))
        self.assertIsNone(parse_size("abcGB"))


class TestGenerateLines(unittest.TestCase):
    def test_same_seed_same_lines(self) -> None:
        self.assertEqual(first_lines(7, 1000), first_lines(7, 1000))

    def test_lines_end_with_newline(self) -> None:
        for line in first_lines(7, 1000):
            self.assertTrue(line.endswith("\n"))

    def test_errors_come_from_known_clients(self) -> None:
        allowed = set(UNSTABLE_CLIENTS) | set(ATTACKERS)
        allowed = allowed | set(HOME_IPS.values())
        for line in first_lines(7, 20000):
            fields = line.split(" | ")
            if len(fields) == 6 and fields[1] == "ERROR":
                ip = fields[3].strip()
                if not ip.startswith("300"):
                    self.assertIn(ip, allowed)

    def test_ssh_users_connect_from_their_own_ip(self) -> None:
        for line in first_lines(7, 20000):
            fields = line.split(" | ")
            if len(fields) == 6 and fields[2] == "sshd":
                ip, user = fields[3], fields[4]
                if ip in ATTACKERS or ip.startswith(("300", " ")):
                    continue
                if user in HOME_IPS:
                    self.assertEqual(ip, HOME_IPS[user])


if __name__ == "__main__":
    unittest.main()
