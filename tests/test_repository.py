"""Repository, relative link, documentation and intended locale checks."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_skill.py"
SPEC = importlib.util.spec_from_file_location("symbolic_validator", VALIDATOR)
assert SPEC and SPEC.loader
VALIDATE_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE_MODULE)


class RepositoryTests(unittest.TestCase):
    def test_local_validator(self) -> None:
        self.assertEqual(VALIDATE_MODULE.validate(), [])

    def test_json_schema_is_wellformed(self) -> None:
        schema = json.loads((ROOT / "assets/draw.schema.json").read_text(encoding="utf-8"))
        self.assertIn("schema_version", schema["required"])
        self.assertIn("provenance", schema["required"])
        self.assertIn("local_system_random", schema["properties"]["provenance"]["properties"]["source"]["enum"])

    def test_six_languages_appear_in_reference_guide(self) -> None:
        s = (ROOT / "references/languages.md").read_text(encoding="utf-8")
        for marker in ("English", "简体中文", "日本語", "Français", "Español", "Português"):
            with self.subTest(marker=marker):
                self.assertIn(marker, s)

    def test_publication_instructions_avoid_real_account_or_fake_release(self) -> None:
        s = (ROOT / "PUBLISHING.md").read_text(encoding="utf-8")
        self.assertIn("OWNER", s)
        self.assertIn("Topics", s)
        self.assertIn("not", s)


if __name__ == "__main__":
    unittest.main()
