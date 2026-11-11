import contextlib
import io
import unittest

from logengine.cli import parse_args

SAMPLE = ["--files", "data/sample.log"]


class TestParseArgs(unittest.TestCase):
    def test_defaults(self) -> None:
        args = parse_args(SAMPLE)
        self.assertEqual(args.threshold, 3)
        self.assertEqual(args.blacklist, "data/blacklist.txt")
        self.assertIsNone(args.audit)
        self.assertEqual(parse_args([]).files, ["data/sample.log"])

    def test_refuses_bad_values(self) -> None:
        for extra in (["--threshold", "0"], ["--threshold", "trois"]):
            with self.subTest(extra=extra):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        parse_args(SAMPLE + extra)

    def test_refuses_missing_file(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_args(["--files", "absent.log"])


if __name__ == "__main__":
    unittest.main()
