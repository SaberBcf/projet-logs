import unittest

from tests.fixtures import EXPECTED, TEST_LOGS, fake_logs


class TestFixtures(unittest.TestCase):
    def test_total(self) -> None:
        self.assertEqual(len(TEST_LOGS), EXPECTED["total"])

    def test_fake_logs_gives_fresh_copies(self) -> None:
        first = next(fake_logs())
        first["level"] = "CHANGED"
        self.assertEqual(TEST_LOGS[0]["level"], "ERROR")


if __name__ == "__main__":
    unittest.main()
