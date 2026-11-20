---
name: symbolic-reflection-support
description: "Multilingual Agent Skill for Tarot, I Ching 易经, BaZi 八字四柱, 24 solar terms 节气, western natal astrology and grounded emotional self-reflection. Use for 今日牌/今日卦, offline Tarot/hexagram draws, verified birth-chart longitudes, late-Zi day-boundary checks, ten-year luck-cycle arithmetic, relationship reflection or six-language symbolic prompts. Python scripts report inputs, actual ephemeris engine and uncertainty; no scientific fate predictions."
license: AGPL-3.0-or-later
compatibility: "Python 3.10+ for Tarot/I Ching offline stdlib; BaZi, 24 solar terms and natal charts require optional Swiss Ephemeris Python binding (AGPL). Default functions run offline; optional JPL audit performs explicit HTTPS requests on public test dates only. Birth data must remain private; model predictions not scientific."
metadata:
  version: "1.3.5"
  category: "symbolic-reflection"
---

# Symbolic Reflection Support

Help people use cultural symbols as **prompts for self-reflection**, not proof of destiny, health, compatibility or another person's feelings. Ground actionable advice in the person's own account and observable events. Match the user's language and level of depth. When asked for a reading, provide the interpretation without becoming evasive; label its symbolic basis clearly.

## Route the request

1. **Daily Tarot / 今日牌 / 今日のカード / Carte du jour / Carta del día / Carta do dia:** reuse a recorded result for the same method and local date in the current conversation, unless a new draw is requested. Otherwise run a real local one-card draw. A generic daily reading defaults to Tarot.
2. **I Ching / 今日卦 / 六爻:** use the supplied hexagram or six line values, or run an actual three-coin cast. **Six lines are recorded bottom-to-top.** If asked to interpret a historical passage, verify the text before quoting it.
3. **Birth chart, astrology, BaZi, Zi Wei Dou Shu, numerology:** distinguish a user-supplied chart, a verified calculation and a hypothetical example. **v1.3 provides real optional ephemeris calculations for tropical natal charts, 24 solar terms and BaZi pillars / conventional luck cycles** (instructions below). For Zi Wei Dou Shu, precise forecasting or unsupported chart systems, do not fabricate. Obtain calendar, historical time zone, city coordinates and chosen conventions. See [astronomy computation](references/astronomy-computation.md) and [calculation boundaries](references/calculation-boundaries.md).
4. **Relationships, personal reflection, MBTI and color:** listen first; distinguish the user's facts, interpretations and tentative hypotheses. Do not diagnose, type someone from chat, infer a partner's intentions or claim compatibility as fact. Consult [MBTI and color](references/mbti-and-color.md) when relevant.
5. **Quotes and original writing:** verify an actual quotation from its source and distinguish it from paraphrase/translation/original text. See [relationship quotes](references/relationship-quotes.md).
6. **How to start / 怎么玩 / 使い方:** use the [participant guide](references/reading-guide.md); short multilingual aliases are in [short commands](references/short-commands.md).

## Windows PowerShell 5.1 audit and UTF-8 fix (v1.3.5-rc2)

- Emit multilingual reflection CLI output as UTF-8; test harness captures stdout with explicit UTF-8, independent of Windows cp936.
- For NASA audit integrity, **never** compare `manifest.files[].raw_sha256` against `Get-FileHash horizons_*.json` directly: the former hashes raw HTTP payload, whereas the latter hashes a JSON wrapper. Run `python scripts/check_horizons_hashes.py --archive .horizons-audit`. Old v1.3.5-rc1 archives report `PASS_RAW_ONLY_LEGACY`; new ones check `archived_json_sha256` as well. Internal hashes alone do not reauthenticate the original NASA HTTPS connection.
- Preserve `.horizons-audit` before replacing the skill; do not bundle the private raw responses or licensed Swiss satellite ephemeris files.
- User-reported live Windows NASA audit of 12 matched-target comparisons is not equivalent to a repeatable verification of the original HTTPS session in this packaged release.

## Critical Windows/Python 3.13 compatibility (v1.3.5-rc1)

The user's Windows Python 3.13 uses community `pysweph`, not legacy `pyswisseph`. Both import as `swisseph`, but **`calc_ut()` / `deltat_ex()` / `houses_ex()` have incompatible return ABI**. All computation and verification code routes through [`scripts/swiss_compat.py`](scripts/swiss_compat.py); do not use bare `(pos, flags) = swe.calc_ut(...)` or assume `len(cusps)==12`. See [binding compatibility](references/pysweph-compatibility.md).

```powershell
py -3 -m pip install -r requirements-astronomy.txt
py -3 scripts/install_diagnostics.py --require-astronomy
py -3 scripts/fetch_horizons.py --check-center-ephe --swiss-ephe-path "$env:USERPROFILE\.swisseph\ephe"
```

For the final NASA comparison, **only after local Swiss checks pass**:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows-jpl-audit.ps1
```

This opt-in script asks for a contact and requests only public neutral epochs from the official NASA/JPL host. It compares Moon↔301, Swiss PLUTO barycenter↔9, and Swiss 9999 body center↔999. If direct data are unavailable, state **NOT VERIFIED**, not successful. It saves a raw-response evidence package if retrieval succeeds; does not transmit personal birth data.

## Draw accurately (Python 3.10+)

Resolve `scripts/draw.py` **relative to this skill's installed directory**, not the user's project working directory:

```bash
python scripts/draw.py tarot --count 1
python scripts/draw.py tarot --count 3 --reversals
python scripts/draw.py iching
python scripts/draw.py iching --lines 7 8 7 9 7 8
# Reproducible DEMO ONLY; do not describe as an unseeded random reading:
python scripts/draw.py tarot --count 1 --seed 2026
```

Only say **“I drew/cast ...”** after a real tool execution returned a usable result. Report the **exact** card, orientation or six coin sums, primary hexagram, moving lines and resulting hexagram. For user-supplied inputs say **“you supplied ...”**; for `--seed` say **“deterministic demonstration”**. Never substitute a made-up card/hexagram for a failed tool call. If execution is unavailable, say so and offer to interpret user-supplied cards/lines or provide a clearly labeled reflection without drawing.

`draw.py` emits JSON with `schema_version`, `provenance` (source, timestamp and digest) and backward-compatible `cards` / `primary` / `resulting` fields. **The digest proves only consistency of the shown payload, not fairness or supernatural accuracy.** Do not transmit or record personal birth information in random-draw logs. See [traceability](references/traceability.md) for the exact provenance semantics. The Python scripts use the standard library and make no network calls. The optional browser demo has no external assets or persistence; hosting providers may keep their own access logs.

## Interpret with the v1.2 locale catalogs

Use `scripts/reflect.py` to combine the **same real local draw engine** with authored, short, language-specific self-reflection cues from `data/tarot.json` (78 cards × upright/reversed × six languages) or `data/iching.json` (64 King Wen hexagrams × six languages). These are **newly written themes**, not translations of classical I Ching line texts or scientific psychological profiles. Read details in [catalog guidance](references/catalog-and-localization.md).

```bash
# Readable results for humans, JSON for agents (--json):
python scripts/reflect.py tarot --count 1 --lang zh --json
python scripts/reflect.py tarot --count 3 --reversals --lang en
python scripts/reflect.py iching --lang ja --json
python scripts/reflect.py iching --lines 7 8 7 9 7 8 --lang fr
# User-specified, NOT a random draw:
python scripts/reflect.py card --id rws-15 --orientation reversed --lang zh
python scripts/reflect.py hexagram --number 49 --lang zh
# Only for a person with an interactive terminal (never in unattended tool calls):
python scripts/reflect.py wizard --lang zh
```

`reflect.py` wraps the original `draw.py` outcome unchanged (including the v1.1 schema and outcome SHA-256 digest) and adds separate `reading` fields, localized themes, source markers, and a data catalog fingerprint. **Do not include interpretation text when recalculating the draw digest.** Use the `--json` output for programmatic use and default readable output for a terminal user. `--seed` is still **a deterministic demo**; supplied cards, coins or hexagrams are **not draws**. Browser demo: open [`docs/index.html`](docs/index.html) locally. Its independent browser Web Crypto outcomes must be identified as browser outcomes, not as Python executions.


## Calculate BaZi, 24 solar terms and western natal charts (optional, v1.3)

**Astronomical calculation is distinct from symbolic interpretation**. Use real executed JSON outputs; never invent exact pillars, longitudes, house placements, or dates when the runtime lacks the dependency.

Install the optional **AGPL-licensed** engine on a local, authorized Python environment (automatic legacy/new wrapper selection; see [LICENSING.md](LICENSING.md)):

```bash
python -m pip install -r requirements-astronomy.txt
python scripts/solar_terms.py --year 2024 --tz Asia/Shanghai --verify-bisection
python scripts/bazi.py --datetime 2024-02-10T12:00:00 --tz Asia/Shanghai --lat 39.9042 --lon 116.4074 --compare-boundaries
python scripts/natal.py --datetime 2000-01-01T12:00:00 --tz Europe/London --lat 51.4779 --lon 0 --houses placidus --cross-check
```

Those are **neutral public test inputs**, not the user's birth data. The commands make no network requests; do not post users' birth charts to public GitHub logs. Do not infer locations or sex from conversation metadata. BaZi defaults to **midnight day boundary / civil clock**; `--day-boundary zi-start|split-zi`, `--clock mean-solar|apparent-solar`, `--uncertainty-minutes`, `--direction forward|backward` and `--traditional-sex` are explicit conventions, not universally correct choices. Natal default is **tropical + Moshier offline + Placidus**, with optional whole-sign houses. For a Swiss-file backend request `--ephemeris swieph --strict-ephemeris` rejects silent fallback. The `--cross-check` report identifies if the **same effective Moshier engine** was used twice; that is *not* independent validation. Precise natal charts remain sensitive to birth time and DST.

**Report input accuracy, time zone, chosen conventions, actual engine flags and computational limitations.** 22 official 2024 solar-term **dates** (not exact minute times) are independently cross-checked with the Hong Kong Observatory calendar; full 10-planet JPL third-party validation remains outstanding. [Methods, reference sources and limitations](references/astronomy-computation.md). The new v1.3 tools are not part of the no-dependency v1.2 browser demo.

## Independent model comparison and real installation checks (v1.3.1)

Before claiming the natal/calendrical computation is numerically validated, run a **different calculation model**, not another call into the same Swiss library:

```bash
python scripts/verify_ephemeris.py --strict
python scripts/install_diagnostics.py --require-astronomy
```

`verify_ephemeris.py` independently calculates 9/10 natal body longitudes (Sun, Moon, Mercury–Neptune), the Ascendant and Midheaven using NASA/JPL public low-accuracy Keplerian elements, truncated lunar harmonics, and standalone sidereal/horizon formulas. It compares against Swiss/Moshier under **explicit, loose, model-appropriate tolerances**. **Pluto and exact DE440/Horizons remain unverified by this low-precision model; Placidus house cusps are tested independently in v1.3.2.** The reference model is **not** DE440. See [independent QA protocol](references/independent-qa.md).

If a user supplies an actual **external** JPL Horizons observer quantity #31, geocentric ecliptic-of-date, UTC dataset, the `compare_horizons_fixture.py` tool can check a JSON-transcribed copy. Treat uploaded/typed reference provenance as **user-supplied, not authenticated**, and do not synthesize supposedly external values from Swiss. See [independent QA protocol](references/independent-qa.md).

Actual Windows user acceptance testing must run **on the user's Windows/Codex computer**, after installation:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows-smoke-test.ps1 -CheckCodexInstalled
```

This creates a separate venv and will install pinned dependencies with pip; check the script before running. A Linux smoke test does **not** constitute a passed Windows test. The local JSON report is private and excludes birth profiles, hostnames, user names and file paths. See [installation testing protocol](references/install-testing.md).

## Reading structure

For a short daily reading, deliver **(a)** source and exact symbol, **(b)** one concise interpretive theme and why that symbol fits it, **(c)** one proportionate action for today. For deeper requests, discuss multiple possible interpretations and clearly mark which is inferred versus supplied by the person. Follow the requested method and do not add repetitive caveats in every sentence. Respect the user's language (English default, 简体中文, 日本語, français, español, português), including regional varieties. See [language examples](references/languages.md).

For a multi-method comparison, keep each method's inputs separate, explicitly distinguish actual runs from illustrations, and describe differences without suggesting that agreement between symbols scientifically verifies a claim. See [reading methods](references/reading-methods.md) and [example cases](references/example-cases.md).

## Reality checks, safety and privacy

- Symbolic readings are entertainment, cultural exploration and self-reflection. Do not promise outcomes or fixed romantic, financial, health, legal or career events. Use verifiable evidence and qualified help for consequential decisions.
- Acknowledge strong emotions without encouraging dependence on readings or repeated draws for certainty. When uncertainty or repetitive reassurance requests become distressing, redirect gently to the underlying concern and one real-world action.
- In reports of coercion, stalking, violence or fear of retaliation, prioritize safety, trusted help and local emergency resources when immediately necessary; never encourage risky confrontation because a card suggests it.
- Avoid clinical diagnosis, treatment claims, inferred personal attributes and predictions about third parties. Ask only for personal details necessary for the chosen method; prefer local computation. Birth date, time and city are sensitive personal information in context: do not ask the user to post them publicly.
- Voice commands work only if the host supplies a transcription; this skill does **not** capture audio.

Detailed guidelines: [ethics and safety](references/ethics-and-safety.md), [interpretation methods](references/reading-methods.md), [relationship reflections](references/example-cases.md).


## v1.3.2: independent precision checks (NOT fate prediction)

For independent Placidus semiarc house verification, run:
`python scripts/verify_placidus.py --strict`.
This checks 12 cusps across 12 public non-personal epochs/locations (144 results)
against an implementation that does not import Swiss, with a separate
astronomical orientation approximation. Restrict assertions to latitude
[-60,+60] and declared 2 arcsecond full model tolerance. A geometry-only
cross-check using Swiss ARMC/obliquity is NOT an independent astronomy result.

For JPL Horizons geocentric apparent Moon and Pluto, the user must explicitly
authorize the official network query:
`python scripts/fetch_horizons.py --fetch --strict --contact YOUR_CONTACT@example.com --output-dir horizons-audit-output`.
The script saves raw official HTTPS API responses, target IDs, JD UTC/UT epochs,
request URL, SHA256 and numeric comparison; it exits nonzero if network or
parsing fail. Run `--from-archive horizons-audit-output --strict` to recompute
an existing export (archived provenance is not reauthenticated). **If no actual
NASA/JPL response has been received, report NOT VERIFIED**, even if mock parser
tests passed. JPL Horizons does not produce Placidus house cusps. Keep private
birth inputs off the public JPL request; only neutral public test epochs are used.


## Corrected JPL Pluto target identity (audit candidate v1.3.3-rc1)

For independent Horizons checks, **Swiss default PLUTO means Pluto-system barycenter**, so compare to **Horizons target 9**. `999` is Pluto body center and must never be compared to default Swiss as if target-identical. Use [the target audit protocol](references/jpl-target-verification.md) and only report official-source verification after actual JPL HTTPS data have been retrieved and compared. `scripts/fetch_horizons.py` now explicitly distinguishes `Moon`, `PlutoBarycenter`, and `PlutoCenter`; the latter can be independently paired with target 9 when both official responses exist, but Swiss target ID `9999` needs a separately obtained `sat/sepm9999.se1` ephemeris file; `FLG_CENTER_BODY` is not sufficient. The current sandbox **has not downloaded original official Horizons results**.

## v1.3.4-rc1: official data and Pluto-body-center acceptance gates

**Correct computation identity:** Swiss default `PLUTO=9` is the Pluto system barycenter,
matched to Horizons `COMMAND='9'`. Swiss physical Pluto center is a **distinct**
body `ipl=9999` (requires separately licensed `sat/sepm9999.se1`); compare it to
Horizons `COMMAND='999'` only when that file is installed and the true Swiss engine
flag confirms no fallback. Never try to obtain it by setting `FLG_CENTER_BODY` on
Swiss `PLUTO`. See [official closure checklist](references/official-closure-checklist.md).

```bash
# Network-free self-test only. Requires independently obtained Swiss satellite file.
python scripts/fetch_horizons.py --check-center-ephe --swiss-ephe-path PATH_TO_EPHE_ROOT

# Real official JPL attempt using neutral public epochs (no private birth inputs).
# JPL fair use requires your email or HTTPS project URL in the User-Agent.
python scripts/fetch_horizons.py --fetch --strict \
  --contact https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY \
  --targets Moon PlutoBarycenter PlutoCenter --output-dir horizons-audit-output

# With licensed Swiss Pluto center file: add to the previous command:
# --compare-swiss-center --swiss-ephe-path PATH_TO_EPHE_ROOT
```

A DNS failure, missing binary, missing JPL raw response, or mock fixture must
**not** be called official acceptance. The script persists `manifest.json`
with `OFFICIAL_FETCH_INCOMPLETE` when a target fetch fails. `--from-archive`
rechecks archived numbers without reauthenticating original NASA provenance.
