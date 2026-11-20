

## v1.3.5 — 2026-11-20 (Stable Release)

First stable public release of Symbolic Reflection Support.

### Features
- Multilingual Tarot and I Ching reflection tools.
- 78 Tarot cards and 64 I Ching hexagrams.
- Six-language symbolic interpretation catalog.
- BaZi Four Pillars and solar-term calculations.
- Western natal astronomy and Placidus houses.
- Offline interactive browser demonstration.

### Verification
- 117 automated tests passed on Windows.
- All 9 GitHub Actions CI jobs passed.
- Python 3.13 and pysweph compatibility verified.
- Independent astronomical calculation checks.
- JPL Horizons Moon and Pluto numerical audit
  reported successful on Windows.

### Stability and Security
- Fixed Windows UTF-8 compatibility.
- Fixed Swiss Ephemeris Python ABI differences.
- Added separate SHA-256 verification scopes.
- Preserved scientific and symbolic boundaries.
- Excluded private data and proprietary
  satellite ephemeris files from distribution.

This stable release is based on v1.3.5-rc2.
No changes to the core astronomical algorithms.

---

## v1.3.5-rc2 — 2026-11-20 (Windows verification fix; local artifact only)

- Fix real Windows `pysweph` compatibility test proxy, including `calc_ut` 2/3 return values, `houses_ex` 12/13 cusps, and `deltat_ex` scalar/tuple. Do **not** change the verified astronomical computation formulas.
- Normalize multilingual reflection CLI output to UTF-8 and specify UTF-8 for captured subprocess output in tests and diagnostics; add CP936-override regression.
- Fix Windows `sat\sepm9999.se1` slash-regex assertion.
- Add two distinct integrity scopes: `raw_sha256` of original HTTP response bytes and `archived_json_sha256` of the saved JSON wrapper. Provide stdlib-only `scripts/check_horizons_hashes.py` for old/new archives; legacy manifests are explicitly `PASS_RAW_ONLY_LEGACY`, not falsely marked corrupted.
- Remove a stale `fetch_failure.json` after a later *successful* live audit.
- New hash-scope tampering tests ensure modified payload/wrapper is detected. No NASA JPL response, email, birth date, or proprietary Swiss satellite data shipped.
- User-provided Windows console report records online 12/12 official-target comparisons and 4 JPL Pluto 9/999 pair checks, but this release does not itself reauthenticate a remote TLS session or provide independent attestation.

## v1.3.5-rc1 — 2026-11-20

- Cross-version Swiss wrapper adapter for `pyswisseph` (two-value calc, 12 cusps) and `pysweph` (three-value calc, 13 cusps) including `deltat_ex`.
- Python 3.13 installs `pysweph` Win64 wheel instead of compiling old `pyswisseph` with MSVC.
- Install diagnostics identify the actual imported Python binding, not only the Swiss C version.
- Official JPL opt-in Windows audit covers Moon 301, Pluto barycenter 9, body center 999, with Swiss 9999 and real file engine required.
- No official JPL raw response in the development environment; official comparison stays pending.

# Changelog


## 1.3.4-rc1 — 2026-11-20 (corrected center-body implementation; official-source acceptance still open)

- Fix optional Swiss Pluto center call: body ID **9999**, not `PLUTO` plus `FLG_CENTER_BODY` (the earlier v1.3.3-rc1 code was incorrect).
- Add opt-in offline `--check-center-ephe` with required licensed `sat/sepm9999.se1`, strict engine flag and file SHA256; no satellite binary is bundled.
- Require a real contact email or HTTPS project URL for official JPL API queries; add error manifest for partial fetch and transient HTTP retry guard.
- Retain distinct observer targets Moon 301, Pluto system barycenter 9 and Pluto physical center 999 and prohibit source-provenance inflation.
- Add new tests, English/Chinese installation and independent-acceptance instructions, and manual GitHub Actions fair-use identification.
- Remaining OPEN: official raw NASA fetch, numerical JPL 9/999 pairing, actual Swiss center-data test, real Windows host acceptance.

## 1.3.3-rc1 — 2026-11-20 (audit protocol candidate; NOT official JPL certified)

- Corrected a real v1.3.2 target-identity mismatch: default Swiss PLUTO system barycenter must match Horizons **9**, not Pluto **999** body center.
- Changed default opt-in official audit to request Moon **301**, Pluto barycenter **9**, and Pluto body center **999** as three separately identified targets.
- Added a direct official-Horizons 9-vs-999 same-time **spherical** angular-offset test, with sample-specific 1″ threshold, plus fail-closed Swiss CENTER_BODY comparison that requires `sepm9999.se1`.
- Added tests rejecting the old ambiguous Pluto identifier, target-spoofed headers, body-center fallback to barycenter, and mismatched JPL epoch pairs.
- **Official direct-fetch audit is still OPEN:** the sandbox cannot resolve the JPL host. This release candidate does not contain or claim official JPL original responses.


## 1.3.2 — 2026-11-20

- Added Swiss-free numerical Placidus calculation `placidus_independent.py` and dedicated 12-case / 144-cusp cross-check `verify_placidus.py`. 144/144 pass with independent approximate sky orientation, maximum discrepancy about 0.43 arcseconds over public nonpolar cases. A geometry-only control using Swiss ARMC/obliquity is separately labeled as not independent astronomical validation.
- Added opt-in official JPL Horizons `fetch_horizons.py` tool for Moon (301) and Pluto (999), observer quantity 31, public test epochs, request URI, raw API response, SHA-256 and separate Swiss/Moshier comparison. Archive recheck is supported with explicit weaker provenance.
- Added dedicated manually triggered GitHub Actions JPL audit; regular CI remains offline. Added parser/fail-closed and geometry tests.
- **JPL official data unavailable in current runtime: DNS request failed. Moon/Pluto high-precision external acceptance remains OPEN.** No simulated JPL values were substituted.
- Preserved v1.3.1 and earlier functionality, AGPL license, six-language catalog and offline browser demo.

## 1.3.1 — 2026-11-20

- Added a separately implemented, **low-precision** reference model for 8 JPL Table-1 planetary/geocentric longitudes + truncated Moon harmonics, plus independent ASC/MC geometry; six public epochs (66 checks, explicit loose tolerances). **Not** a high-precision DE-series or JPL Horizons comparison.
- Added `scripts/verify_ephemeris.py`, `scripts/compare_horizons_fixture.py`, documented external-fixture schema and negative tests preventing invented NASA/JPL verification claims. Pluto and full Placidus cusp validation remain open.
- Added `scripts/install_diagnostics.py` and opt-in PowerShell Windows isolated-venv testing script; no birth information, username, hostname or IP in its JSON report. **Actual end-user Windows installation remains pending.**
- Added independent QA documentation, real-user installation acceptance checklist, and CI regression commands for the new modules. Existing v1.3 calculators and v1.2 Tarot/I Ching data are unchanged.

## 1.3.0 — 2026-11-20

- Added **optional, locally executable Swiss Ephemeris / Moshier** astronomical calculation modules, without bundling third-party binaries or proprietary ephemeris data.
- `solar_terms.py`: 24 apparent-tropical-Sun-longitude crossings, separate bisection root checks; **22 official 2024 HKO calendar-date fixtures** for cross-checks, not claims of minute-by-minute independent ephemeris validation.
- `bazi.py`: LiChun year, 12 jie month, public 60-day anchor, explicit midnight / 子初 / 晚子时 rules, civil/mean/apparent solar clocks, DST fold and gap checks, optional 10-year luck-cycle arithmetic with direction and nominal start age stated transparently.
- `natal.py`: geocentric tropical Sun–Pluto apparent longitudes, ASC/MC, Placidus/whole-sign houses, time uncertainty samples, **effective ephemeris detection** and honest cross-check status when Swiss ephemeris falls back to Moshier.
- Added independent published calendar-date regression tests, CLI tests, dependency/license documentation and a split GitHub Actions optional-astronomy job.
- **License change:** combined v1.3 distribution now uses AGPL-3.0-or-later due to Swiss Ephemeris integration; prior MIT v1.2 grant remains intact; see `LICENSING.md`.
- Preserved all v1.2 Tarot/I Ching data, offline browser demo and backward-compatible result schemas. **Not included:** full external JPL comparison of all planets, exhaustive calendar school coverage, Zi Wei Dou Shu computational engine, scientific destiny prediction, or repository publication.


## 1.2.0 — 2026-11-20

- Added **78×2×6 original Tarot reflection cues**, including localized card names, upright and reversed themes in Simplified Chinese, English, Japanese, French, Spanish, Portuguese.
- Added **64×6 original hexagram reflection themes**, keyed by canonical King Wen number and Chinese name. **Not** a translation of classical Judgment/Image/line texts.
- Added `scripts/reflect.py` for human-readable or JSON multilingual readings, source-tagged interpretation of user-selected cards and hexagrams, and a human-only optional terminal wizard.
- Added `docs/index.html`: standalone responsive offline web demo, Web Crypto Tarot / I Ching simulations, six-language UI, card/hexagram browsing and user-exported JSON without network dependencies.
- Added separate reading schema and data-quality checks; preserved the original `draw.py` **schema 1.1** for compatibility.
- Updated skill workflow and English/Chinese documentation, public GitHub Pages steps, privacy/safety notes and CI tests.
- **Not included:** a BaZi or astronomy computation engine, full classical text corpus, scientific predictions, browser-to-Python attestations, or deployment to a live GitHub repository.


## 1.1.0 — 2026-11-20

- Preserved the original Tarot and I Ching commands, 78-card deck, King Wen mapping and six-language conversational references.
- Added the source-tagged JSON result envelope (`schema_version`, tool version, UTC timestamp and SHA-256 outcome fingerprint).
- Added stable Tarot card identifiers and Simplified Chinese names.
- Added explicitly labeled deterministic `--seed` mode for reproducible demonstrations, not for live readings.
- Added decoding of six user-supplied rows of three coins with `--coins`.
- Added source-specific tracing, chart-calculation boundaries, ethics guidance and evaluation scenarios.
- Added bilingual GitHub README, publishing checklist, contributor and security notes, examples, stdlib tests, local validator and GitHub Actions CI.
- **Not included:** an ephemeris, BaZi calculation engine, voice capture, third-party API, guaranteed host-agent compatibility or verified predictions.

## Initial upload — 2026-11-19

- Original `SKILL.md`, six-language references, `scripts/draw.py`, README and MIT license.
