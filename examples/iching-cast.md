# Example: supplied I Ching line values

```bash
python scripts/draw.py iching --lines 7 8 7 9 7 8
```

Input: six values from **bottom to top**; values `6/7/8/9` represent old yin / young yang / young yin / old yang (respectively). The script reports:

- Primary hexagram: **49 革**, lower trigram Li, upper Dui
- Moving lines: **4** (old yang `9` changes to yin)
- Resulting hexagram: **63 既济**, lower Li, upper Kan
- `provenance.source`: `user_supplied_lines`

**Do not say this cast was simulated or randomly tossed.** The user supplied the data. An interpretation might use the traditional theme of changing an old arrangement while maintaining the order that follows. Verify any classical quote against a chosen source edition.

For a true simulated three-coin cast, run:

```bash
python scripts/draw.py iching
```

For six individually recorded coin triples, use `--coins` followed by 18 values, three for each line from bottom up:

```bash
python scripts/draw.py iching --coins 3 2 2  2 3 2  3 2 2  3 3 3  2 2 3  3 2 2
```
