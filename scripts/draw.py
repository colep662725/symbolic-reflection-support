#!/usr/bin/env python3
"""Offline Tarot draw and I Ching three-coin cast. Outputs JSON, no network or PII.

Compatibility: Python 3.10+. The original v1.0 card/hexagram fields are retained.
Default draws use SystemRandom; --seed is an explicitly labeled deterministic demo.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import random
from secrets import SystemRandom
from typing import Any

VERSION = "1.2.0"
SCHEMA_VERSION = "1.1"
MAJOR = (
    "The Fool", "The Magician", "The High Priestess", "The Empress",
    "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
    "Strength", "The Hermit", "Wheel of Fortune", "Justice",
    "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower",
    "The Star", "The Moon", "The Sun", "Judgement", "The World",
)
MAJOR_ZH = (
    "愚者", "魔术师", "女祭司", "皇后", "皇帝", "教皇", "恋人", "战车",
    "力量", "隐者", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔",
    "高塔", "星星", "月亮", "太阳", "审判", "世界",
)
SUITS = ("Wands", "Cups", "Swords", "Pentacles")
SUITS_ZH = ("权杖", "圣杯", "宝剑", "星币")
RANKS = (
    "Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
    "Nine", "Ten", "Page", "Knight", "Queen", "King",
)
RANKS_ZH = (
    "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
    "侍从", "骑士", "皇后", "国王",
)
DECK = MAJOR + tuple(f"{rank} of {suit}" for suit in SUITS for rank in RANKS)
DECK_ZH = MAJOR_ZH + tuple(f"{suit}{rank}" for suit in SUITS_ZH for rank in RANKS_ZH)

# I Ching bit patterns are bottom-to-top, with yang=1 and yin=0.
TRIGRAMS = {
    (1, 1, 1): "Qian", (1, 1, 0): "Dui", (1, 0, 1): "Li",
    (1, 0, 0): "Zhen", (0, 1, 1): "Xun", (0, 1, 0): "Kan",
    (0, 0, 1): "Gen", (0, 0, 0): "Kun",
}
TRIGRAM_ORDER = ("Qian", "Dui", "Li", "Zhen", "Xun", "Kan", "Gen", "Kun")
# Rows are lower trigrams and columns are upper trigrams.
KING_WEN = (
    (1, 43, 14, 34, 9, 5, 26, 11),
    (10, 58, 38, 54, 61, 60, 41, 19),
    (13, 49, 30, 55, 37, 63, 22, 36),
    (25, 17, 21, 51, 42, 3, 27, 24),
    (44, 28, 50, 32, 57, 48, 18, 46),
    (6, 47, 64, 40, 59, 29, 4, 7),
    (33, 31, 56, 62, 53, 39, 52, 15),
    (12, 45, 35, 16, 20, 8, 23, 2),
)
HEXAGRAM_NAMES = (
    "乾", "坤", "屯", "蒙", "需", "讼", "师", "比", "小畜", "履", "泰", "否",
    "同人", "大有", "谦", "豫", "随", "蛊", "临", "观", "噬嗑", "贲", "剥", "复",
    "无妄", "大畜", "颐", "大过", "坎", "离", "咸", "恒", "遁", "大壮", "晋", "明夷",
    "家人", "睽", "蹇", "解", "损", "益", "夬", "姤", "萃", "升", "困", "井", "革", "鼎",
    "震", "艮", "渐", "归妹", "丰", "旅", "巽", "兑", "涣", "节", "中孚", "小过", "既济", "未济",
)


def describe_hexagram(bits: tuple[int, ...]) -> dict[str, Any]:
    """Describe a six-bit pattern, ordered bottom-to-top."""
    if len(bits) != 6 or any(bit not in (0, 1) for bit in bits):
        raise ValueError("a hexagram must have exactly six yin/yang bits")
    lower, upper = TRIGRAMS[bits[:3]], TRIGRAMS[bits[3:]]
    number = KING_WEN[TRIGRAM_ORDER.index(lower)][TRIGRAM_ORDER.index(upper)]
    return {"lower": lower, "upper": upper, "number": number, "name_zh": HEXAGRAM_NAMES[number - 1]}


def draw_tarot(rng: random.Random | SystemRandom, count: int, reversals: bool) -> dict[str, Any]:
    """Sample from all 78 cards without replacement."""
    if not 1 <= count <= 78:
        raise ValueError("card count must be between 1 and 78")
    indices = rng.sample(range(len(DECK)), count)
    return {
        "method": "Rider-Waite-Smith card names, sampled without replacement",
        "cards": [
            {
                "id": f"rws-{index:02d}", "card": DECK[index],
                "card_zh": DECK_ZH[index],
                "orientation": "reversed" if reversals and rng.randrange(2) else "upright",
            }
            for index in indices
        ],
    }


def decode_lines(values: list[int] | tuple[int, ...]) -> dict[str, Any]:
    """Decode 6/7/8/9 coin sums, bottom line first."""
    if len(values) != 6 or any(v not in (6, 7, 8, 9) for v in values):
        raise ValueError("supply six line values from {6,7,8,9}, bottom-to-top")
    primary_bits = tuple(value % 2 for value in values)
    moving = [i for i, value in enumerate(values, 1) if value in (6, 9)]
    changed_bits = tuple(1 - bit if value in (6, 9) else bit
                         for bit, value in zip(primary_bits, values))
    return {
        "moving_lines_from_bottom": moving,
        "primary": describe_hexagram(primary_bits),
        "resulting": describe_hexagram(changed_bits) if moving else None,
    }


def cast_iching(rng: random.Random | SystemRandom) -> dict[str, Any]:
    coins = [[rng.choice((2, 3)) for _ in range(3)] for _ in range(6)]
    return decode_coin_rows(coins, method="three coins per line, tails=2, heads=3")


def decode_coin_rows(coins: list[list[int]], method: str) -> dict[str, Any]:
    """Preserve all 18 heads/tails values for audit/replay."""
    if len(coins) != 6 or any(len(row) != 3 or any(c not in (2, 3) for c in row) for row in coins):
        raise ValueError("provide six rows of three coins, each 2 or 3")
    values = [sum(row) for row in coins]
    return {
        "method": method,
        "coins_bottom_to_top": coins,
        "line_values_bottom_to_top": values,
        **decode_lines(values),
    }


def provenance(payload: dict[str, Any], source: str, seed: int | None = None) -> dict[str, Any]:
    """Digest is a consistency fingerprint, not proof of randomness."""
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    result = {
        "source": source,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "payload_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        "digest_scope": "all top-level outcome fields, excluding schema/tool version and provenance",
    }
    if seed is not None:
        result["seed"] = seed
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="method", required=True)
    tarot = subparsers.add_parser("tarot", help="Draw Tarot cards, default 3")
    tarot.add_argument("--count", type=int, default=3)
    tarot.add_argument("--reversals", action="store_true", help="Allow reversed orientations")
    tarot.add_argument("--seed", type=int, help="For reproducible DEMOS/TESTS only")
    iching = subparsers.add_parser("iching", help="Cast or decode a six-line hexagram")
    supplied = iching.add_mutually_exclusive_group()
    supplied.add_argument("--lines", nargs=6, type=int, choices=(6, 7, 8, 9), metavar="N",
                          help="Six coin sums from bottom to top")
    supplied.add_argument("--coins", nargs=18, type=int, choices=(2, 3), metavar="N",
                          help="18 individual coin values, bottom row first")
    iching.add_argument("--seed", type=int, help="For reproducible DEMOS/TESTS only")
    args = parser.parse_args()
    if args.method == "tarot" and not 1 <= args.count <= 78:
        parser.error("card count must be between 1 and 78")
    if args.method == "iching" and args.seed is not None and (args.lines or args.coins):
        parser.error("--seed cannot be combined with supplied lines or coins")
    rng = random.Random(args.seed) if args.seed is not None else SystemRandom()

    if args.method == "tarot":
        outcome = draw_tarot(rng, args.count, args.reversals)
        source = "seeded_demo" if args.seed is not None else "local_system_random"
    elif args.lines is not None:
        outcome = {
            "method": "user-supplied line values",
            "line_values_bottom_to_top": args.lines,
            **decode_lines(args.lines),
        }
        source = "user_supplied_lines"
    elif args.coins is not None:
        rows = [args.coins[i * 3:(i + 1) * 3] for i in range(6)]
        outcome = decode_coin_rows(rows, method="user-supplied coin values, tails=2, heads=3")
        source = "user_supplied_coins"
    else:
        outcome = cast_iching(rng)
        source = "seeded_demo" if args.seed is not None else "local_system_random"

    result = {
        "schema_version": SCHEMA_VERSION,
        "tool_version": VERSION,
        **outcome,
        "provenance": provenance(outcome, source, args.seed),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
