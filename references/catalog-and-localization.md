# Six-language catalog and interpretation boundaries (v1.2)

The skill bundles two **original** reflection catalogs, both stored as UTF-8 JSON:

- `data/tarot.json`: 78 cards, stable `rws-00`...`rws-77` identifiers, name in `en`/`zh`/`ja`/`fr`/`es`/`pt`, and **individual upright and reversed prompts** in the same six languages.
- `data/iching.json`: all 64 hexagrams in King Wen sequence. The canonical Chinese name and disambiguating number are authoritative fields for matching the `draw.py` mapping; pinyin is for convenience. Each has a short **independently authored reflection theme** in six languages.

These are **deliberately brief** themes, *not* a complete reproduction or scholarly translation of the Rider–Waite–Smith guidebook or the Yijing, Judgment, Image, and moving-line texts. They avoid asserting future outcomes, health diagnoses, a stranger's feelings or fortune.

## Provenance-first interpretation

1. Determine whether the symbol is from a **real tool execution**, a **seeded demo**, a **user-supplied card/line/hexagram** or an **illustration**.
2. Verify the actual IDs, line order, orientation and moving lines before looking up meaning. I Ching: bottom-to-top 6/7/8/9 values; 6 and 9 are moving.
3. Use the **selected language** and the catalog cue appropriate to the orientation or hexagram number. `reflect.py` does not claim classical textual quotations. When a user specifically asks for classical line text, check a suitable primary source first.
4. Invite **one real-world reflection** or modest action; don't repeat draws to relieve anxiety and don't treat an independent random draw as evidence about fate.
5. Distinguish a short *theme* from a complete individualized reading. Deeper readings require user-provided context and should not infer facts about another person.

## Programmatic calls

```bash
python scripts/reflect.py tarot --count 1 --lang zh --json
python scripts/reflect.py tarot --count 3 --reversals --lang fr --json
python scripts/reflect.py iching --seed 2026 --lang en --json  # demo, NOT unseeded
python scripts/reflect.py iching --lines 7 8 7 9 7 8 --lang ja --json
python scripts/reflect.py card --id rws-00 --orientation reversed --lang pt --json
python scripts/reflect.py hexagram --number 63 --lang es --json
```

- `raw_result`: v1.1 drawing fields and provenance. `draw.py` remains backwards compatible.
- `reading`: locale-specific wording plus `catalog_sha256`; **not** part of the raw draw digest.
- `reading_version`: catalog wrapper version `1.2.0`.
- The interactive wizard is only for people with a real terminal. Agents should use the noninteractive CLI.
- The browser demo, `docs/index.html`, uses **Web Crypto** to simulate the same 3-coin distribution, but is an **independent random generator** with `source=browser_webcrypto`. `user_selected_*` values in the browser are never represented as draws.

## Translation and QA

All six locale rows are present and tested for nonblank fields; QA does **not** guarantee perfect idiomatic terminology. Translations and proposed corrections are welcome with an explanation and test. The card labels are cultural labels and vary by edition and country. The original script's English deck and Chinese card names remain the stable identifiers for compatibility.

No personal birth information is stored in catalogs or sent to any service. Host-agent conversations and public GitHub Pages visits have their own independent retention/logging policies.
