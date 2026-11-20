"""stdlib-only unit and CLI smoke tests for symbolic-reflection-support."""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DRAW = ROOT / "scripts" / "draw.py"
SPEC = importlib.util.spec_from_file_location("symbolic_draw", DRAW)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def invoke(*arguments: str) -> dict:
    completed = subprocess.run([sys.executable, str(DRAW), *arguments],
                               capture_output=True, text=True, check=True)
    return json.loads(completed.stdout)


class TarotTests(unittest.TestCase):
    def test_deck_has_78_unique_names_and_chinese_names(self) -> None:
        self.assertEqual(len(MODULE.DECK), 78)
        self.assertEqual(len(set(MODULE.DECK)), 78)
        self.assertEqual(len(MODULE.DECK_ZH), 78)
        self.assertEqual(len(set(MODULE.DECK_ZH)), 78)

    def test_all_cards_without_replacement(self) -> None:
        result = MODULE.draw_tarot(random.Random(1), 78, reversals=True)
        self.assertEqual(len(result["cards"]), 78)
        self.assertEqual({c["card"] for c in result["cards"]}, set(MODULE.DECK))
        self.assertEqual({c["id"] for c in result["cards"]},
                         {f"rws-{i:02d}" for i in range(78)})
        self.assertTrue(all(c["orientation"] in ("upright", "reversed")
                            for c in result["cards"]))

    def test_no_reversal_by_default(self) -> None:
        result = MODULE.draw_tarot(random.Random(2), 12, False)
        self.assertTrue(all(c["orientation"] == "upright" for c in result["cards"]))

    def test_deterministic_demo_is_reproducible(self) -> None:
        a, b = invoke("tarot", "--count", "3", "--reversals", "--seed", "2026"), \
               invoke("tarot", "--count", "3", "--reversals", "--seed", "2026")
        self.assertEqual(a["cards"], b["cards"])
        self.assertEqual(a["provenance"]["payload_sha256"], b["provenance"]["payload_sha256"])
        self.assertEqual(a["provenance"]["source"], "seeded_demo")
        self.assertEqual(a["provenance"]["seed"], 2026)

    def test_known_seeded_demo(self) -> None:
        result = invoke("tarot", "--count", "1", "--seed", "2026")
        self.assertEqual(result["cards"][0]["card"], "The Devil")
        self.assertEqual(result["cards"][0]["card_zh"], "恶魔")
        self.assertEqual(result["cards"][0]["id"], "rws-15")

    def test_default_random_source(self) -> None:
        result = invoke("tarot", "--count", "1")
        self.assertEqual(result["provenance"]["source"], "local_system_random")
        self.assertNotIn("seed", result["provenance"])

    def test_invalid_card_counts_fail(self) -> None:
        for count in ("0", "79", "-1"):
            with self.subTest(count=count):
                p = subprocess.run([sys.executable, str(DRAW), "tarot", "--count", count],
                                   text=True, capture_output=True)
                self.assertNotEqual(p.returncode, 0)
                self.assertIn("card count", p.stderr)


class IChingTests(unittest.TestCase):
    def test_all_64_yinyang_patterns_map_to_exactly_64_king_wen_numbers(self) -> None:
        all_hexagrams = [MODULE.describe_hexagram(bits)
                         for bits in itertools.product((0, 1), repeat=6)]
        self.assertEqual({h["number"] for h in all_hexagrams}, set(range(1, 65)))
        self.assertEqual(len(set(MODULE.HEXAGRAM_NAMES)), 64)

    def test_eight_pure_trigrams_have_expected_king_wen_numbers(self) -> None:
        pure = {"Qian": 1, "Dui": 58, "Li": 30, "Zhen": 51,
                "Xun": 57, "Kan": 29, "Gen": 52, "Kun": 2}
        for bits, trigram in MODULE.TRIGRAMS.items():
            with self.subTest(trigram=trigram):
                self.assertEqual(MODULE.describe_hexagram(bits + bits)["number"], pure[trigram])

    def test_three_coin_outcome_combinatorics(self) -> None:
        distribution = {v: 0 for v in (6, 7, 8, 9)}
        for coins in itertools.product((2, 3), repeat=3):
            distribution[sum(coins)] += 1
        self.assertEqual(distribution, {6: 1, 7: 3, 8: 3, 9: 1})

    def test_known_hexagrams(self) -> None:
        self.assertEqual(MODULE.describe_hexagram((1,) * 6)["number"], 1)
        self.assertEqual(MODULE.describe_hexagram((0,) * 6)["number"], 2)
        parsed = MODULE.decode_lines([7, 8, 7, 9, 7, 8])
        self.assertEqual(parsed["primary"]["number"], 49)
        self.assertEqual(parsed["primary"]["name_zh"], "革")
        self.assertEqual(parsed["moving_lines_from_bottom"], [4])
        self.assertEqual(parsed["resulting"]["number"], 63)
        self.assertEqual(parsed["resulting"]["name_zh"], "既济")

    def test_older_reference_case(self) -> None:
        parsed = MODULE.decode_lines([7, 8, 6, 7, 8, 9])
        self.assertEqual(parsed["primary"]["number"], 21)
        self.assertEqual(parsed["resulting"]["number"], 55)
        self.assertEqual(parsed["moving_lines_from_bottom"], [3, 6])

    def test_no_moving_lines_has_null_resulting(self) -> None:
        self.assertIsNone(MODULE.decode_lines([7, 8, 7, 8, 7, 8])["resulting"])

    def test_each_moving_line_flips_only_one_bit(self) -> None:
        for position in range(6):
            values = [7] * 6
            values[position] = 9
            result = MODULE.decode_lines(values)
            self.assertEqual(result["moving_lines_from_bottom"], [position + 1])
            self.assertNotEqual(result["resulting"], result["primary"])

    def test_three_coin_rows_reproduce_recorded_values(self) -> None:
        sample = MODULE.cast_iching(random.Random(42))
        self.assertEqual(len(sample["coins_bottom_to_top"]), 6)
        for row, value in zip(sample["coins_bottom_to_top"], sample["line_values_bottom_to_top"]):
            self.assertEqual(len(row), 3)
            self.assertTrue(all(c in (2, 3) for c in row))
            self.assertEqual(sum(row), value)
        self.assertEqual(sample["primary"], MODULE.decode_lines(sample["line_values_bottom_to_top"])["primary"])

    def test_supplied_lines_and_coins_have_distinct_sources(self) -> None:
        line_result = invoke("iching", "--lines", "7", "8", "7", "9", "7", "8")
        self.assertEqual(line_result["provenance"]["source"], "user_supplied_lines")
        self.assertNotIn("coins_bottom_to_top", line_result)
        coins = [3, 2, 2, 2, 3, 2, 3, 2, 2, 3, 3, 3, 2, 2, 3, 3, 2, 2]
        coin_result = invoke("iching", "--coins", *map(str, coins))
        self.assertEqual(coin_result["provenance"]["source"], "user_supplied_coins")
        self.assertEqual(coin_result["line_values_bottom_to_top"], [7, 7, 7, 9, 7, 7])

    def test_invalid_coins_lines_and_incompatible_flags_rejected(self) -> None:
        cases = [
            ("iching", "--lines", "1", "2", "3", "4", "5", "6"),
            ("iching", "--coins", "2", "3"),
            ("iching", "--lines", "7", "8", "7", "9", "7", "8", "--seed", "1"),
            ("iching", "--lines", "7", "8", "7", "9", "7", "8", "--coins", *["2"] * 18),
        ]
        for args in cases:
            with self.subTest(args=args):
                p = subprocess.run([sys.executable, str(DRAW), *args], text=True, capture_output=True)
                self.assertNotEqual(p.returncode, 0)


class ProvenanceTests(unittest.TestCase):
    def test_digest_matches_outcome_and_is_not_over_personal_data(self) -> None:
        for result in (invoke("tarot", "--count", "1", "--seed", "123"),
                       invoke("iching", "--seed", "123"),
                       invoke("iching", "--lines", "7", "8", "7", "9", "7", "8")):
            payload = {k: v for k, v in result.items()
                       if k not in ("schema_version", "tool_version", "provenance")}
            encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            self.assertEqual(hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
                             result["provenance"]["payload_sha256"])
            self.assertEqual(result["schema_version"], "1.1")
            self.assertEqual(len(result["provenance"]["payload_sha256"]), 64)
            self.assertNotIn("birth", json.dumps(result).lower())


if __name__ == "__main__":
    unittest.main()
