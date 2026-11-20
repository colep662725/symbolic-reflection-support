
> **Current Stable Release: v1.3.5 (2026-11-20)**
>
> Symbolic Reflection Support is a multilingual
> Agent Skill for Tarot, I Ching, BaZi, Western
> astrology, and responsible self-reflection.
>
> **Validation:**
> - 117 automated tests passed on Windows.
> - All 9 GitHub Actions CI jobs passed.
> - Supports Python 3.10–3.13.
> - Compatible with pyswisseph and pysweph.
> - Includes Swiss Ephemeris astronomical calculations.
> - Includes JPL Horizons verification tools.
>
> **Scientific note:** Astronomical calculations
> can be independently verified. Symbolic readings
> are not scientifically validated predictions.
>
> Historical changes are documented in CHANGELOG.md.

# Symbolic Reflection Support

> **Historical v1.3.4-rc1 (2026-11-20):** Correct Swiss Pluto body-center target to **9999**, not default `PLUTO` plus `FLG_CENTER_BODY`. Add mandatory contact for opt-in JPL queries, failure-preserving manifests, local satellite-file diagnostics and expanded regression tests. **Official live NASA responses and the actual `9` vs `999` comparison remained open at that release; the user has since reported a successful Windows Swiss `9999` calculation.** See the [strict acceptance checklist](references/official-closure-checklist.md) and [QA report](QA_REPORT.md).


**Open-source multilingual Agent Skill for Tarot, I Ching, verifiable BaZi calendar calculations, Western natal astronomy and grounded personal reflection.**

[简体中文](README.zh-CN.md) · [Offline browser demo (Tarot/I Ching)](docs/index.html) · [Agent Skills](https://agentskills.io/specification) · [AGPL-3.0-or-later](LICENSE) · [Licensing notice](LICENSING.md)

**v1.3.0** added three **real local calculation tools** built on an explicitly pinned Swiss Ephemeris / Moshier engine: 24 solar-term crossings, Four Pillars BaZi with configurable time-boundary rules and conventional ten-year luck-cycle arithmetic, and tropical Western natal charts (ten planetary longitudes, ASC/MC, houses). Inputs, selected rules, actual library engine, uncertainties and limitations are **reported in JSON**. The existing v1.2 multilingual Tarot/I Ching experience remains intact.

**v1.3.2 verification update:** Added **Swiss-free mathematical Placidus verification** covering all 12 cusps across 12 public non-personal cases (**144/144**, maximum difference **0.431 arcseconds** using independently approximated sky orientation). Geometry-only bisection using Swiss ARMC/obliquity matches to below 0.001 arcseconds, but is not an independent *astronomical* comparison. Added a live, opt-in official JPL Horizons Moon/Pluto downloader that archives original HTTPS responses and checksums, plus a manual GitHub Actions audit. **Actual JPL responses have NOT been downloaded in the present restricted environment, so the external high-precision Moon/Pluto validation remains OPEN.** [Validation methodology](references/independent-qa.md) · [Windows installation acceptance protocol](references/install-testing.md).

> **Reality check:** calculation accuracy is distinct from metaphysical validity. We can verify astronomical longitudes and calendar rules; we **cannot** scientifically establish that an astrological or BaZi chart predicts personality, love, money, health, marriage, or destiny.

## Quick start

**Tarot / I Ching (stdlib-only; Python 3.10+):**

```bash
python scripts/reflect.py tarot --count 1 --lang zh
python scripts/reflect.py tarot --count 3 --reversals --lang en
python scripts/reflect.py iching --lang ja
python scripts/reflect.py iching --lines 7 8 7 9 7 8 --lang zh
python scripts/draw.py tarot --count 1   # previous JSON schema v1.1 is unchanged
```

**Astronomy and BaZi (one-time optional AGPL dependency, stays offline):**

```bash
python -m pip install -r requirements-astronomy.txt

# Actual 24 solar terms, Sun-longitude checks and IANA timezone conversion
python scripts/solar_terms.py --year 2024 --tz Asia/Shanghai --verify-bisection

# Public sample date; LiChun year + jie month, explicit midnight and late Zi conventions
python scripts/bazi.py --datetime 2024-02-10T12:00:00 --tz Asia/Shanghai --lat 39.9042 --lon 116.4074 --compare-boundaries

# Traditional ten-year luck cycles are optional: specify direction, not inferred sex
python scripts/bazi.py --datetime 2024-02-10T12:00:00 --tz Asia/Shanghai --lat 39.9042 --lon 116.4074 --direction forward --cycles 8

# Tropical, geocentric apparent Sun–Pluto; explicit Placidus or whole-sign houses
python scripts/natal.py --datetime 2000-01-01T12:00:00 --tz Europe/London --lat 51.4779 --lon 0 --houses placidus --cross-check --uncertainty-minutes 15
```

These use **neutral public test inputs**, never private natal data. Every calculation is machine-readable JSON to stdout. Local time requires an IANA timezone and explicit latitude/longitude; no silent geocoding, remote birth-data API or birth-profile logging.

## What works and what is still limited?

| Feature | v1.3 capability | Important scope |
| --- | --- | --- |
| Tarot | 78 cards; upright/reversed six-language original themes; real offline draws | Cultural reflection, not prediction |
| I Ching | Three-coin casts, King Wen 64 hexagrams, moving-line transformations; six-language original themes | No classic Judgment/Image text corpus; provenance distinguishes real draw/demo/user input |
| BaZi / 四柱 | LiChun year; 12 `jie` month boundaries; 60-day anchors; hour-stem calculation; configurable `midnight`, `zi-start`, `split-zi`, civil/mean/apparent solar clocks | Multiple schools exist; output does not determine a unique universally accepted chart |
| 大运 | Opt-in forward/backward direction, next/previous `jie`, 3 days/nominal year and transparent approximate start, 10-year pillar sequence | **Conventional arithmetic**, not objectively good/bad luck predictions |
| 24 solar terms | Apparent Sun-longitude crossings, local calendar dates, separate root bisection check | 22 HKO 2024 **date-level** comparisons; exact independent-minute precision not certified |
| Natal astrology | Ten apparent tropical body longitudes, ASC/MC, Placidus/whole-sign houses, ephemeris fallback detection, birth-time sensitivity | **9/10 bodies + ASC/MC** now have independent **low-precision** model QA; Pluto and direct JPL DE-series comparison remain open; all 12 Placidus cusps have independent geometry/model comparisons at 12 nonpolar reference cases |
| Provenance | Effective Moshier vs Swiss engine, exact rules and UTC timestamp of inputs, consistency checks | **Moshier compared to itself is NOT independent verification** |
| Browser demo | Responsive six-language Tarot / I Ching HTML in `/docs` (no API, cookies, tracking) | **Does not compute BaZi or natal charts in browser** |

### About accuracy and licensing

- The **default** uses Moshier algorithms **inside** Swiss Ephemeris; it works without `.se1` ephemeris files. `--ephemeris swieph` may silently fall back to Moshier **inside the third-party library**. Results report the effective engine. Use `--strict-ephemeris` to fail when requested Swiss files are unavailable.
- `natal.py --cross-check` runs the other requested engine and reports whether the effective engines really differ; a comparison using Moshier twice is **not** an independent cross-check. Bisection and the built-in solar longitude crossing are two root-solving paths over the **same** astronomical model.
- Reference tests compare the model's 22 February–December 2024 solar-term **calendar dates** against the [Hong Kong Observatory's official 2024 calendar](https://www.hko.gov.hk/tc/gts/time/calendar/pdf/files/2024.pdf). Day/month/hour stem relationships use [HKO's stems/branches tables](https://www.hko.gov.hk/sc/gts/time/stemsandbranches.htm) and public 2000 / 2024 day anchors. A **second, independently implemented low-precision JPL-element model** has now passed 66 comparisons, but independent full-precision JPL Horizons/DE-series verification has **not** been completed. See [independent QA](references/independent-qa.md).
- **License change:** v1.3 combined repo is **AGPL-3.0-or-later**, due to the new `pyswisseph` integration. **Earlier MIT v1.2 rights are unchanged.** Read [LICENSING.md](LICENSING.md) before reuse, especially in a networked service. Swiss Ephemeris separately offers a Professional License.
- None of the arithmetic establishes the future predictive or psychological accuracy of fortune telling. Keep private birth details out of public GitHub Issues or CI fixtures. See [full calculation conventions](references/astronomy-computation.md).

## Independent QA and real installation (v1.3.2)

```bash
# 66 model-level independent-reference comparisons; outputs traceable JSON
python scripts/verify_ephemeris.py --strict

# Privacy-conscious diagnosis; fails if optional astronomy extra is missing
python scripts/install_diagnostics.py --require-astronomy

# All 12 Placidus cusps, 12 public cases = 144 checks using independent geometry
python scripts/verify_placidus.py --strict

# EXPLICIT opt-in internet access: fetch genuine Moon + Pluto data from NASA/JPL
# Only neutral public dates, no private birth details. Saves raw response + SHA256.
python scripts/fetch_horizons.py --fetch --strict --contact YOUR_CONTACT@example.com --output-dir horizons-audit-output

# Repeat the comparison against downloaded raw archives (local, provenance not reauthenticated)
python scripts/fetch_horizons.py --from-archive horizons-audit-output --strict

# Alternative manual fixture: numerically compare user-supplied values without authenticating them
python scripts/compare_horizons_fixture.py --file PATH_TO_EXTERNAL_REFERENCE.json --strict
```

On a **real Windows PC**, run the opt-in `scripts/windows-smoke-test.ps1` from an actual extracted installation. It creates a fresh venv and installs pinned dependencies via pip; it does not collect natal records. The command and the limits of a clean-room Windows test are documented in [installation testing](references/install-testing.md). This package has **not** been tested on your Windows PC or published GitHub Actions yet.

## Install as an Agent Skill

Place this directory at a location your Agent recognizes, e.g. `%USERPROFILE%\.codex\skills\symbolic-reflection-support\` on Windows, then use `$symbolic-reflection-support` if your host supports skill activation. The bot should load [`SKILL.md`](SKILL.md) and, when needed, [calculation instructions](references/astronomy-computation.md), [reading guide](references/reading-guide.md), or [ethics guidance](references/ethics-and-safety.md). A chat Project instruction alone does **not** provide executable access to Python.

Once a public repo is actually available (replace `OWNER` with the *real* GitHub username):

```bash
npx skills add OWNER/symbolic-reflection-support --list
npx skills add OWNER/symbolic-reflection-support --skill symbolic-reflection-support
```

## Run tests

```bash
# Always available with standard library
python scripts/validate_skill.py
python scripts/build_demo.py --check
python -m unittest discover -s tests -v

# For complete ephemeris tests (not just skips), install optional dependency first
python -m pip install -r requirements-astronomy.txt
python -c "import swisseph; print(swisseph.version)"
python -m unittest tests.test_astronomy tests.test_independent_qa -v

# Optional independently installed Agent Skills reference validator
skills-ref validate .
```

CI includes a cross-platform **base job** (no optional astronomy dependency; astronomy tests skip) and an **optional astronomy job** (pinned dependency actually installed and mandatory). The latter verifies 24 roots, 22 official HKO date comparisons, 60-day cycles, explicit school policies, DST gaps/overlaps, ephemeris fallback status and planetary regression. These are **engineering tests**, not fortune-telling validation.

## Publish and contribute

See [`PUBLISHING.md`](PUBLISHING.md) for a copy-ready GitHub Description, Topics, release and Pages checklist. Generating a ZIP **does not upload, update or index a repository**. See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), and [`CHANGELOG.md`](CHANGELOG.md). The v1.2 demo remains no-dependency and can be opened offline; no natal information is collected from the demo.


## JPL Pluto target correction — v1.3.3-rc1 audit candidate

**Important correction to v1.3.2:** default Swiss `PLUTO` is Pluto-system **barycenter**. Its aligned Horizons target is `9`, not `999` (Pluto **body center**). In the corrected opt-in audit, Moon 301 and Pluto barycenter 9 are compared to Swiss; separately fetched official Pluto 9 and 999 positions are compared to each other as a spherical angular offset. The latter needs direct official data; no such responses were obtained in this sandbox. Swiss body-center target **9999** additionally requires licensed `sat/sepm9999.se1` files; the previous `FLG_CENTER_BODY` approach was incorrect. See [the protocol](references/jpl-target-verification.md).

```bash
python scripts/fetch_horizons.py --fetch --strict --contact YOUR_CONTACT@example.com --targets Moon PlutoBarycenter PlutoCenter --output-dir horizons-audit-output
python scripts/fetch_horizons.py --from-archive horizons-audit-output --strict --targets Moon PlutoBarycenter PlutoCenter
```

This is a verification **release candidate**, not a completed NASA/JPL-certified high-precision release.

## v1.3.4-rc1 — physical Pluto center computation (offline and opt-in)

```bash
python scripts/fetch_horizons.py --check-center-ephe --swiss-ephe-path EPHE_ROOT
python scripts/fetch_horizons.py --fetch --strict --contact YOUR_CONTACT@example.com --targets Moon PlutoBarycenter PlutoCenter --output-dir horizons-audit-output
# After installing licensed sat/sepm9999.se1, add --compare-swiss-center --swiss-ephe-path EPHE_ROOT
```

No Swiss satellite binary, official JPL response or private birth record is included in the release ZIP.


## v1.3.5-rc1 Windows Python 3.13 repair and final JPL audit

If you previously installed `pysweph` on Windows and saw `too many values to unpack`, this release fixes the calculation return ABI **throughout** natal, BaZi, solar terms, the 12 Placidus cusps and the Horizons audit. Do not edit the library C code or reinstall Python just to work around the wrapper mismatch.

```powershell
py -3 -m pip install --only-binary=:all: -r requirements-astronomy.txt
py -3 scripts/install_diagnostics.py --require-astronomy
py -3 scripts/fetch_horizons.py --check-center-ephe --swiss-ephe-path "$env:USERPROFILE\.swisseph\ephe"
powershell -ExecutionPolicy Bypass -File .\scripts\windows-jpl-audit.ps1
```

The last command is **opt-in**: it asks for a real contact email/project URL and queries only four public dates. Do not claim the JPL audit has passed based only on these commands existing. Current network-restricted build cannot resolve NASA API; use the user-side manifest and original JSON to complete official closure.
