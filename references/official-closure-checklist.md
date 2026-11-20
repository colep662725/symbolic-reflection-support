> **v1.3.5-rc1 state:** Swiss Moon/barycenter/9999 basic calculations **user-reported PASS on Windows**. Our newer wrapper was exercised against the real legacy library and a simulated modern ABI. **Not closed:** direct NASA/JPL raw API response, same-epoch official 9 vs 999 angular offset, official 999 vs local Swiss 9999 error. Use the new `scripts/windows-jpl-audit.ps1` when JPL network is reachable; see [compatibility](pysweph-compatibility.md).

# Official ephemeris verification — closure protocol (v1.3.4-rc1)

> **Status on 2026-11-20:** The NASA live-source and Pluto center/barycenter full acceptance are **NOT YET COMPLETE** in this workspace. Mock data are never official evidence. Successful local code tests are not official NASA ephemerides.

## Three separate targets

| Requested object | JPL Horizons command | Swiss target (pyswisseph) | Prerequisite |
|---|---|---|---|
| Moon center | 301 | `swe.MOON` | Moshier offline works |
| Pluto-system barycenter | 9 | `swe.PLUTO` | Moshier offline works |
| Physical Pluto body center | 999 | **`9999`** | Licensed `sat/sepm9999.se1` and any other required Swiss ephemeris files |

Swiss `9999` is a separate planetary-moon/center body ID (Swiss Ephemeris v2.10+). **Do not use** `swe.calc_ut(..., swe.PLUTO, swe.FLG_CENTER_BODY)` as a substitute: that is not an independent body-ID selection. The program requires `FLG_SWIEPH` in the result when target `9999` is requested.

Swiss docs: https://www.astro.com/swisseph/swephprg.htm (see *Planetary moons and body centers*); https://www.astro.com/ftp/swisseph/ephe/sat/. The satellite file is NOT bundled and must be sourced under its own applicable terms.

## Step 1: independently acquire and validate Swiss data

Get `sepm9999.se1` from the official Astrodienst Swiss Ephemeris satellite-data collection or its [official upstream GitHub file](https://github.com/aloistr/swisseph/blob/master/ephe/sat/sepm9999.se1), if permitted by its terms. The GitHub repository contains the file, but this release does not redistribute it. Place under:

```text
EPHE_ROOT/
└── sat/
    └── sepm9999.se1
```

Other Swiss planetary ephemeris files may also be required by the installed version. The relevant center-body data cover approximately 1900–2047, not the entire 1900–2100 range advertised for standard natal planet computations.

```bash
python scripts/fetch_horizons.py --check-center-ephe --swiss-ephe-path EPHE_ROOT
```

A success prints `PASS_SWISS_9999_LOCAL_ONLY`, the file SHA256, and four **neutral** epoch center positions. This is **not** a JPL comparison. A missing file, unsupported date or unexpected backend fails closed.

## Step 2: official JPL live data (opt-in and sequential)

Install requirements and run from this skill directory with your own real contact email **or actual public HTTPS repository URL**; the contact is sent in `User-Agent` in accordance with the JPL API fair-use policy. No private birth time/place is queried: the code uses four fixed neutral UTC epochs only.

```bash
python -m pip install -r requirements-astronomy.txt
python scripts/fetch_horizons.py --fetch --strict \
  --contact https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY \
  --targets Moon PlutoBarycenter PlutoCenter \
  --output-dir horizons-audit-output
```

Optional, after completing Step 1:

```bash
python scripts/fetch_horizons.py --fetch --strict \
  --contact YOUR_CONTACT@example.com \
  --targets Moon PlutoBarycenter PlutoCenter \
  --compare-swiss-center --swiss-ephe-path EPHE_ROOT \
  --output-dir horizons-audit-center
```

The official Horizons requests use `EPHEM_TYPE=OBSERVER`, geocentric `CENTER=500@399`, `QUANTITIES=31`, `TIME_TYPE=UT`, `TLIST_TYPE=JD`, airless apparent ecliptic-of-date longitude/latitude, and fixed public epochs. The program checks the signature, target IDs and Earth-origin header, then saves the exact URL, raw response, and SHA256.

The center-versus-barycenter comparison is a **spherical angular separation** using both longitude and latitude. The default 1 arcsec separation limit is an empirical finite-test threshold, **not** a physical universal bound. Moon and barycenter values are separately compared to Moshier with a configurable 30 arcsec default audit tolerance.

The API must provide a valid response for both `9` and `999` at the same epochs before the JPL pair is closed. The `--compare-swiss-center` mode additionally needs successful Swiss target `9999` values and matches them to Horizons `999`.

## Step 3: archive audit without provenance inflation

```bash
python scripts/fetch_horizons.py --from-archive horizons-audit-output --strict \
  --targets Moon PlutoBarycenter PlutoCenter
```

`--from-archive` verifies the stored response digest, canonical query, identity and numeric consistency. It **does not** reauthenticate source provenance or constitute a new NASA HTTPS fetch. Inspect `manifest.json`, the three `horizons_*_public.json` responses, and SHA256. When a fetch fails, inspect `fetch_failure.json` and a manifest marked `OFFICIAL_ATTEMPT_INCOMPLETE`.

## Acceptance matrix (do not conflate)

| Obligation | Passing evidence | Current claim |
|---|---|---|
| Correct target definitions | Official docs + tests for 301, 9, 999, Swiss 9999 | **Closed** |
| Archive-based Moon / Pluto barycenter | 36 numeric matches in range from third-party JPL-attributed archive | **Secondary numerical crosscheck only** |
| JPL direct Moon and Pluto barycenter | Three genuine live HTTPS responses with source provenance, parsed matching timestamps | **Open** |
| JPL `9` versus `999` same-epoch offset | Genuine official output for both IDs and spherical distance | **Open** |
| Swiss `9999` local computation | Licensed real `sat/sepm9999.se1`, engine flag, sample results | **Open** (file absent here) |
| Swiss `9999` versus official Horizons `999` | Genuine JPL response plus target-matched Swiss output, prescribed tolerances | **Open** |
| User Windows/Codex installation | Actual Windows log and user confirmation | **Open** |

Even if every astronomical test passes, no scientific validation of personal life prediction follows.

## Source and fair use

- JPL API: https://ssd-api.jpl.nasa.gov/doc/horizons.html
- JPL API fair-use: https://ssd-api.jpl.nasa.gov/
- JPL observer quantity 31 and target center conventions: https://ssd.jpl.nasa.gov/horizons/manual.html
- Swiss body center ID 9999, sat data layout and 1900–2047 limits: https://www.astro.com/swisseph/swephprg.htm
