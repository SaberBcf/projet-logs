import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from logengine.audit import describe_scope, export_audit


class TestAudit(unittest.TestCase):
    def test_describe_skips_internal_names(self) -> None:
        report = describe_scope({"__name__": "x", "seuil": 3})
        self.assertEqual(list(report), ["seuil"])
        self.assertEqual(report["seuil"]["type"], "int")

    def test_generator_is_not_consumed(self) -> None:
        numbers = (n for n in range(3))
        describe_scope({"numbers": numbers})
        self.assertEqual(list(numbers), [0, 1, 2])

    def test_export_writes_json(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "audit.json"
            with contextlib.redirect_stdout(io.StringIO()):
                export_audit({"a": 1}, {"b": [1, 2]}, str(path))
            report = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(report["locales"]["b"]["type"], "list")


if __name__ == "__main__":
    unittest.main()
