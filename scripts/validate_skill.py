#!/usr/bin/env python3
"""Dependency-free sanity checks. NOT a substitute for official skills-ref validate."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
NAME = "symbolic-reflection-support"


def validate(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    path = root / "SKILL.md"
    if not path.exists():
        return ["SKILL.md missing"]
    text = path.read_text(encoding="utf-8")
    fm = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
    if not fm:
        return ["SKILL.md must begin with YAML frontmatter"]
    head = fm.group(1)
    fields: dict[str, str] = {}
    # This validator intentionally checks simple scalar fields only. Install
    # `skills-ref` for full YAML/Agent Skills spec validation.
    for line in head.splitlines():
        if line.startswith(" ") or not line.strip():
            continue
        if ":" not in line:
            problems.append(f"Invalid top-level frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"\'')
    name = fields.get("name", "")
    desc = fields.get("description", "")
    if name != NAME or name != root.name:
        problems.append(f"Expected name/directory '{NAME}'")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        problems.append("Invalid skill name syntax or length")
    if not (1 <= len(desc) <= 1024):
        problems.append("Description must be between 1 and 1024 characters")
    if "compatibility" in fields and len(fields["compatibility"]) > 500:
        problems.append("compatibility exceeds 500 characters")
    if fields.get("license") != "AGPL-3.0-or-later":
        problems.append("License metadata should be AGPL-3.0-or-later")
    if 'version: "1.3.5"' not in head:
        problems.append("Expected version 1.3.5 in frontmatter metadata")
    for relative in ("README.md", "README.zh-CN.md", "LICENSE", "scripts/draw.py",
                     "references/reading-methods.md", "assets/draw.schema.json",
                     ".github/workflows/ci.yml", "tests/test_draw.py", "tests/test_catalog.py",
                     "scripts/reflect.py", "scripts/build_demo.py", "data/tarot.json", "data/iching.json",
                     "assets/reading.schema.json", "docs/index.html",
                     "scripts/bazi.py", "scripts/natal.py", "scripts/solar_terms.py", "scripts/calendar_core.py",
                     "tests/test_astronomy.py", "requirements-astronomy.txt", "LICENSING.md",
                     "references/astronomy-computation.md", "assets/bazi.schema.json", "assets/natal.schema.json",
                     "assets/solar-terms.schema.json",
                     "scripts/ephemeris_reference.py", "scripts/verify_ephemeris.py",
                     "scripts/install_diagnostics.py", "scripts/windows-smoke-test.ps1",
                     "scripts/compare_horizons_fixture.py", "tests/test_independent_qa.py",
                     "references/independent-qa.md", "references/install-testing.md",
                     "scripts/placidus_independent.py", "scripts/verify_placidus.py",
                     "scripts/fetch_horizons.py", "tests/test_independent_precision.py",
                     "scripts/swiss_compat.py", "tests/test_swiss_compat.py",
                     "scripts/windows-jpl-audit.ps1", "references/pysweph-compatibility.md",
                     "tests/test_horizons_v134.py", "references/official-closure-checklist.md",
                     "QA_TARGET_IDENTITY.md", "INSTALL.zh-CN.md",
                     ".github/workflows/horizons-audit.yml"):
        if not (root / relative).is_file():
            problems.append(f"Required file missing: {relative}")
    # Only relative links are checked; HTTP references are not fetched.
    for markdown in root.rglob("*.md"):
        source = markdown.read_text(encoding="utf-8")
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", source):
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            pure_path = target.split("#", 1)[0]
            if not pure_path:
                continue
            if not (markdown.parent / pure_path).exists():
                problems.append(f"Broken relative link in {markdown.relative_to(root)}: {target}")
    try:
        schema = json.loads((root / "assets/draw.schema.json").read_text(encoding="utf-8"))
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            problems.append("Unexpected JSON schema version")
    except (OSError, json.JSONDecodeError) as error:
        problems.append(f"Malformed result JSON Schema: {error}")
    try:
        tarot = json.loads((root / "data/tarot.json").read_text(encoding="utf-8"))
        iching = json.loads((root / "data/iching.json").read_text(encoding="utf-8"))
        locales = {"en", "zh", "ja", "fr", "es", "pt"}
        cards = tarot["cards"]
        if len(cards) != 78 or {x["id"] for x in cards} != {f"rws-{i:02d}" for i in range(78)}:
            problems.append("Tarot catalog must contain unique cards rws-00..rws-77")
        for i, card in enumerate(cards):
            if set(card["names"]) != locales or set(card["cues"]) != locales:
                problems.append(f"Missing card locale: {i}")
                continue
            if any(not card["names"][l].strip() or set(card["cues"][l]) != {"upright", "reversed"}
                   or not all(v.strip() for v in card["cues"][l].values()) for l in locales):
                problems.append(f"Missing localized Tarot text: {i}")
        hs = iching["hexagrams"]
        if len(hs) != 64 or [x["number"] for x in hs] != list(range(1,65)):
            problems.append("Hexagram catalog must contain King Wen 1..64")
        for h in hs:
            if set(h["themes"]) != locales or not all(v.strip() for v in h["themes"].values()):
                problems.append(f"Missing hexagram translations: {h['number']}")
        reading_schema = json.loads((root / "assets/reading.schema.json").read_text(encoding="utf-8"))
        if reading_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            problems.append("Unexpected localized reading JSON Schema version")
    except (OSError, ValueError, KeyError, TypeError) as error:
        problems.append(f"Malformed v1.2 catalogs or reading schema: {error}")
    for name in ("bazi.schema.json", "natal.schema.json", "solar-terms.schema.json"):
        try:
            calc_schema = json.loads((root / "assets" / name).read_text(encoding="utf-8"))
            if calc_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                problems.append(f"Bad calculation schema draft: {name}")
            if "schema_version" not in calc_schema.get("required", []):
                problems.append(f"Calculation schema lacks version requirement: {name}")
        except (OSError, ValueError, KeyError, TypeError) as error:
            problems.append(f"Invalid calculation schema {name}: {error}")
    return problems


if __name__ == "__main__":
    issues = validate()
    if issues:
        print("Skill checks FAILED:", file=sys.stderr)
        for issue in issues:
            print(f" - {issue}", file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: {NAME} — frontmatter, required files, relative links, JSON Schema")
    print("NOTE: this is a local sanity check, not a full official skills-ref validation.")
