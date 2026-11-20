# How to interpret draw provenance

The original `draw.py` script returns JSON, and its output remains on schema `1.1` for backward compatibility. The new `reflect.py --json` wrapper keeps the complete draw under `raw_result` and adds `reading_version: 1.2.0` plus `reading` with catalog cues and a `catalog_sha256` fingerprint. Each actual draw or decoding has these **top-level** fields:

- `schema_version`: output schema identifier (`1.1` for this release)
- `tool_version`: the version of the script
- `method`: human-readable convention used
- `cards`, or `coins_bottom_to_top` / `line_values_bottom_to_top` / `primary` / `resulting`: outcome, compatible with the original script
- `provenance.source`: how the outcome was obtained
- `provenance.generated_at_utc`: the UTC timestamp produced by the program
- `provenance.payload_sha256`: SHA-256 over canonical UTF-8 JSON of **outcome fields only**, with sorted keys, compact separators and unescaped Unicode

| Source value | What the user should be told |
| --- | --- |
| `local_system_random` | The Python script was actually executed with its system-provided random source. The outcome is a random simulation, not a prediction |
| `seeded_demo` | A **deterministic demonstration or test**; report the seed if necessary. Do not claim an independent unseeded draw |
| `user_supplied_lines` | The user provided six values 6–9, bottom-to-top; the script decoded them, but did **not** toss coins |
| `user_supplied_coins` | The user provided 18 individual coin values 2/3; the script decoded them, but did **not** toss coins |

## Scope and limitations

The fingerprint can help check if a saved result was copied without modification. It cannot establish that physical coins were tossed, that a random outcome was unbiased, or that the reading is true. No tamper-proof logging, signed attestation or long-term storage is provided by this release. On a new run with the same seeded demo, the **outcome and hash** repeat; the timestamp changes.

No personal details are embedded or written to disk by the CLI. The host AI application may have its own separate retention policies, which are outside the script's control.

## Audit an outcome

1. Preserve the complete JSON returned by the tool (not just the final prose reading).
2. Confirm `source`, method, date, order and any moving lines; I Ching lines are bottom-to-top.
3. Optionally recompute the hash from all fields excluding `schema_version`, `tool_version` and `provenance` using the Python `json.dumps(..., sort_keys=True, separators=(',', ':'), ensure_ascii=False)` convention.
4. Distinguish **script-confirmed data** from the human/AI's **symbolic interpretation**.

Example safe reporting: "You supplied the six line values 7,8,7,9,7,8 from bottom to top. I decoded them using the local script: Hexagram 49 革, fourth line moving, resulting in 63 既济. No random coin toss was performed; the interpretation is symbolic, not a prediction."

## New v1.2 reading-layer sources

`reflect.py` adds two possible user-selected sources to its `raw_result`:

- `user_supplied_card`: a caller explicitly chose a Tarot `rws-XX` and orientation; this **was not randomly drawn**.
- `user_supplied_hexagram`: a caller explicitly chose a King Wen number; this **was not cast with coins**.

All existing `draw.py` sources remain unchanged. The `reading.catalog_sha256` is the hash of the UTF-8 `data/tarot.json` or `data/iching.json` bytes at runtime. This helps identify the version of authored interpretation text used, not its truth or historical authority. A reading's question and theme are *not* included in the original raw-outcome digest.

`docs/index.html` independently simulates Tarot and I Ching in the browser. Its JSON copy output uses `schema_version=browser-demo-1.2` and `source=browser_webcrypto` for browser random draws, or `user_selected_*` for manual browsing. It is **not** interchangeable with the Python draw digest, and it intentionally does not claim that a browser action ran Python.
