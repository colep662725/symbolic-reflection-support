# v1.3 reproducible astronomy / BaZi computation

This document describes **calculations**, not empirically validated personality/fate forecasts. Run the real `scripts/*` and inspect returned JSON; do not fabricate placements, terms, luck-cycle start ages, or independent cross-check status.

## Optional dependency, license and privacy

- Core Tarot/I Ching scripts remain standard-library only. Astronomical modules need `python -m pip install -r requirements-astronomy.txt`; The AGPL Swiss binding is version-pinned per Python version: legacy `pyswisseph==2.10.3.2` on Python <3.13 and compatible modern `pysweph==2.10.3.6` on Python >=3.13. A small adapter normalizes C/Python ABI differences. Read [licensing](../LICENSING.md).
- No network, API key, uploaded natal data, account, or disk-borne personal chart is required. Input is local, output is stdout JSON. **Never publish somebody's natal chart/birth time in public test fixtures or issue reports without explicit consent.**
- Default actual ephemeris is `moseph`, built into the library and usable offline without `.se1` files. `--ephemeris swieph` asks for Swiss data; if missing, the library can **silently fall back**. The code reports the **effective engine** by return flags. `--strict-ephemeris` prevents accepting an unintended fallback.
- A test that asks for Swiss and Moshier but gets Moshier twice is **not independent confirmation**. A root checked by another solver over the same Sun-longitude model is also not an independent ephemeris. Independent published checks: HKO 2024 official **calendar dates** for the 22 solar terms Feb–Dec, and publicly published 2000-01-01 / 2024-02-10 day-cycles. We **have not** independently compared a full ten-planet chart with JPL Horizons in v1.3.
- Ephemeris and longitude values are **model results**. More displayed decimal digits do not imply unlimited physical accuracy; ΔT, historical civil-time records, coordinates and birthplace uncertainty matter.

## BaZi rules used — explicitly switchable

- **Calendar:** proleptic Gregorian civil dates 1900–2100, the `--tz` IANA geographic time zone, `--lat`/`--lon` explicit geographic coordinates; ambiguous DST `--fold 0/1`; non-existent DST clock times rejected. Coordinates are NOT silently looked up from city names.
- **Year:** changes at actual instant the apparent geocentric tropical Sun crosses **315°** (`立春`), not at New Year's Day or lunar New Year. Baseline `1984=甲子` gives the Gregorian solar-cycle year stem/branch.
- **Month:** 12 `jie` terms: 315° 立春, 345° 惊蛰, 15° 清明, 45° 立夏, 75° 芒种, 105° 小暑, 135° 立秋, 165° 白露, 195° 寒露, 225° 立冬, 255° 大雪, 285° 小寒. Month stem: 甲己年丙寅, 乙庚年戊寅, 丙辛年庚寅, 丁壬年壬寅, 戊癸年甲寅; monthly stem/branch advance by one at each `jie`.
- **Day:** civil Gregorian dates count as a continuous 60-day cycle anchored at public almanac **2000-01-01 戊午**, checked independently against public **2024-02-10 甲辰**. A formal rule for the late Zi hour is required:
  - `--day-boundary midnight`: 00:00 changes day, 23:00–23:59 Zi hour uses the same day's stem.
  - `--day-boundary zi-start`: 23:00 changes both day pillar and Zi-hour's reference day.
  - `--day-boundary split-zi`: 23:00–23:59 day pillar stays on civil day while Zi-hour uses the next day's stem. This is one explicit late-Zi convention, **not** a universal rule.
- **Hour branch:** Zi 23:00–00:59, Chou 01–02:59, etc. Hour stem uses `甲己起甲子`/`乙庚起丙子`/`丙辛起戊子`/`丁壬起庚子`/`戊癸起壬子`, with day-stem policy above.
- **Clock:** `--clock civil` is the civil wall clock (default); `mean-solar` applies `longitude/15` correction relative to historical time-zone offset; `apparent-solar` additionally applies Swiss equation-of-time. These are different *school conventions*, not more/less spiritually accurate measurements. They can cross midnight or a branch-hour boundary.
- **Ten-year luck cycles (大运):** no inference of user gender. `--direction forward/backward` explicitly chooses; `--traditional-sex male/female` uses the conventional yin-year/yang-year rule only if the user opts in. Counting from birth to next/previous **jie** respectively: 3 solar days per nominal year, and for *display* a year is modeled as 365.2425 days; start is **approximate** and alternative school conventions can differ. Every 10 nominal years the month pillar moves by one sexagenary step in direction. Do not label a cycle inherently auspicious or predict events.
- **Uncertainty:** `--uncertainty-minutes N` compares endpoint examples but does not certify all times inside the interval; need additional root/branch boundary analysis near transitions. `--compare-boundaries` prints all three late-Zi conventions.

## Western natal chart computation

- Geocentric, apparent, tropical longitude of date, ten bodies Sun..Pluto, default offline Moshier. No sidereal, heliocentric, topocentric chart, nodes, or aspects implemented in v1.3.
- **Angles:** ASC and MC using Swiss `houses_ex` at specified exact UTC, lat and longitude. Choose `--houses placidus` (default) or `--houses whole-sign`. Placidus cannot be computed at some extreme latitudes: fail explicitly, never silently switch.
- **House membership:** compare each body's **ecliptic longitude** to consecutive house cusp longitudes. It is **not** Swiss `house_pos`, which can account for ecliptic latitude. Comparisons close to house boundaries are convention-sensitive. Whole-sign house cusps begin at 0° of the ASC sign.
- `--cross-check`: compute second requested backend and compare positions. When both effective ephemerides are equal, returns `NOT_INDEPENDENT_both_calls_used_same_effective_engine`. Even when distinct, they are two algorithms from **the same Swiss library**; independent third-party astronomy engine validation remains a future task.
- `--uncertainty-minutes`: endpoint calculations for ASC, MC and planet house positions, without presuming birth-time rectification.

## Reproducible CLI examples (neutral public inputs)

```bash
python scripts/solar_terms.py --year 2024 --tz Asia/Shanghai --verify-bisection
python scripts/bazi.py --datetime 2024-02-10T12:00:00 --tz Asia/Shanghai --lat 39.9042 --lon 116.4074 --compare-boundaries --direction forward
python scripts/natal.py --datetime 2000-01-01T12:00:00 --tz Europe/London --lat 51.4779 --lon 0 --houses placidus --cross-check --uncertainty-minutes 15
# Use --ephemeris swieph --strict-ephemeris only if you have legally obtained ephemeris files.
```

## External reference sources

- [HKO 60 stems / branches, year/month/hour rules](https://www.hko.gov.hk/sc/gts/time/stemsandbranches.htm)
- [HKO 2024 calendar, dates of 24 solar terms](https://www.hko.gov.hk/tc/gts/time/calendar/pdf/files/2024.pdf)
- [Swiss Ephemeris programming manual](https://www.astro.com/swisseph/swephprg.pdf)
- [Published 2000-01-01 sexagenary day](https://www.rili.com.cn/wannianli/2000/0101.html)
- [Published 2024-02-10 sexagenary day](https://www.rili.com.cn/wannianli/2024/0210.html)

**Scientific boundary:** astronomical longitudes and term timestamps are empirical/model-based computations; attaching a personality, relationship or future event meaning to them is traditional symbolism, not a scientifically validated prediction.

## v1.3.1 independent **low-precision** check

The independent *implementation* in `scripts/ephemeris_reference.py` uses a NASA/JPL published analytical approximation, a truncated lunar series, and separate sidereal/horizon formulas. Six public epochs give 66 loose-tolerance comparisons. This does **not** establish 10-body high-precision JPL Horizons agreement (Pluto excluded), does **not** fully validate Placidus house cusps, and is not a substitute for authentic external ephemeris export. See [complete verification protocol](independent-qa.md) and [actual-user Windows protocol](install-testing.md).
