# Independent astronomical QA: what is and is not certified

## Purpose

Reject false precision. The `natal.py --cross-check` mode inside Swiss Ephemeris is only a **same-library comparison**, and can silently use the same Moshier analytical engine for both requested backends if Swiss `.se1` files are absent. Do not call that independent verification.

New in v1.3.1: `scripts/verify_ephemeris.py` compares Swiss/Moshier against a second program, implemented in `scripts/ephemeris_reference.py` using **NO Swiss calculation imports**.

## Public sources and comparison frame

1. NASA/JPL SSD **Approximate Positions of the Planets**, Table 1 (1800–2050), heliocentric J2000 element-rate fit: https://ssd.jpl.nasa.gov/planets/approx_pos.html
2. Simplified lunar harmonics derived independently from mean lunar arguments and principal periodic terms (compare classical Meeus lunar series, e.g. https://github.com/architest/pymeeus/blob/master/pymeeus/Moon.py ). This is deliberately not the full lunar theory.
3. Independently coded Greenwich mean sidereal time and geometric ecliptic intersection with the eastern horizon and local meridian for ASC/MC.
4. Reference target: Swiss/Moshier geocentric **apparent tropical ecliptic longitude of date**; independent planetary model is **geometric J2000**, approximately precessed to date with a first-order term. Results have known residual differences from aberration, light time, nutation, Earth/Moon barycenter and the approximation model itself. This is NOT a high-precision JPL ephemeris.

## Offline model-level procedure

```bash
python -m pip install -r requirements-astronomy.txt
python scripts/verify_ephemeris.py --strict > local-model-qa.json
# Custom local time (example uses neutral public test input)
python scripts/verify_ephemeris.py --epoch-utc 2024-06-21T00:00:00+00:00 --lat 35.6762 --lon 139.6503 --strict
```

The default six public epochs compare **9 bodies and 2 angles each = 66 checks**. The declared acceptance tolerances (degrees) are:

| Object | Tolerance |
|---|---:|
| Sun, Mercury, Venus, Uranus, Neptune | 0.20° |
| Moon | 0.35° |
| Mars | 0.25° |
| Jupiter | 0.45° |
| Saturn | 0.50° |
| ASC | 0.10° |
| MC | 0.06° |

These limits are **not forecasts of expected physics-level errors**. They only check that two models are mutually consistent to a coarse threshold on a set of public examples. **Pluto** and the detailed **Placidus intermediate cusps** are not independently validated by this test. Near polar latitudes and at times outside the published JPL Table 1 validity range, the QA tool refuses to extrapolate.

## How to perform a real JPL Horizons cross-check

JPL Horizons API documentation: https://ssd-api.jpl.nasa.gov/doc/horizons.html

- Obtain a **geocentric** Observer table `CENTER='500@399'` for one target at a time (`Sun=10`, `Moon=301`, `Mercury=199`, `Venus=299`, `Mars=499`, `Jupiter=599`, `Saturn=699`, `Uranus=799`, `Neptune=899`, `PlutoBarycenter=9` for default Swiss PLUTO; `PlutoCenter=999` only with explicit center-body computation, where available).
- Request **Observer table QUANTITIES='31'** (`ObsEcLon`): apparent observer-centered Earth-ecliptic-of-date longitude. Select UTC/UT and avoid topocentric/refraction settings. Verify actual target identifier and model in the returned header.
- Retain the source query URL, raw response, date/time time scale, frame and numeric precision **outside a public repo if personal**. Do not paste private birth coordinates or names into public Issues.
- Transcribe only the independent external readings to local JSON using the following shape (values here are placeholders, not real HORIZONS output):

```json
{
  "metadata": {
    "center": "500@399",
    "quantity": "31",
    "coordinate_type": "observer_ecliptic_of_date_apparent",
    "time_scale": "UTC",
    "source_description": "JPL Horizons query + response archived by the tester"
  },
  "observations": [
    {"body": "Mars", "utc": "2024-06-21T00:00:00+00:00", "longitude_deg": 0.0}
  ]
}
```

**The example longitude 0.0 is intentionally false:** it must be replaced with a real independently obtained number. Do not add the placeholder JSON to actual reference benchmarks.

```bash
python scripts/compare_horizons_fixture.py --file PATH_TO_VERIFIED_INPUT.json --tolerance-arcsec 30 --strict
```

The tool reports **USER_SUPPLIED_NOT_AUTHENTICATED** in every case: it can compare numbers but cannot prove that a file really originated from NASA. As of v1.3.2 the **Placidus geometry** has a separate independent numerical check below. **Authentic Horizons/DE440 Moon and Pluto data remains uncollected**; the high-precision independent ephemeris claim is not certified.

## Publication honesty

- Phrases allowed: “independent low-precision model comparison,” “66 model-level checks passed,” “22 official calendar dates independently matched.”
- Phrases NOT supported: “10/10 planets verified against JPL,” “NASA-certified astronomical accuracy,” “Swiss v. JPL high-precision validation passed,” or “astrology scientifically predicts future events.”


## v1.3.2 — independent full Placidus house geometry

Unlike the earlier ASC/MC-only comparison, `scripts/placidus_independent.py` **does not import Swiss**. It computes local apparent sidereal angle using a separate GMST polynomial + a four-term nutation approximation, mean/true obliquity, the eastern ecliptic/horizon intersection, and the four nontrivial Placidus cusps (2,3,11,12) by solving semidiurnal and seminocturnal arc fractions using bracketed bisection. Remaining houses follow 180° opposite cusps.

Run `python scripts/verify_placidus.py --strict`. It compares 12 public dates and latitudes spanning [-60,+60], 144 cusp longitudes total, with independent sky orientation and **2 arcsecond maximum per-cusp acceptance**. In a second intentionally separate experiment it holds Swiss ARMC and obliquity fixed and checks only independent cusp geometry at a stringent 0.01 arcsecond tolerance. The second experiment is not independent astronomy; the first does not meet SOFA/IAU sub-milliarcsecond precision, nor does either establish polar circle/alternative house-system correctness.

Method reference: https://kerykeion.net/libephemeris/docs/reference/house-systems (semiarc thirds). This package independently re-implements the geometric defining equations, not the upstream program's code.

## v1.3.2 — real NASA/JPL Horizons data protocol (still external-data-dependent)

The exact **official** live API query is generated by `scripts/fetch_horizons.py`. It requests:

- `COMMAND='301'` (Moon), `COMMAND='9'` (Pluto-system barycenter, aligned with Swiss default PLUTO), and `COMMAND='999'` (Pluto body center, separate JPL-only pair check), separately;
- `CENTER='500@399'` (Earth geocenter), `EPHEM_TYPE='OBSERVER'`;
- `QUANTITIES='31'` = apparent observer ecliptic-of-date longitude/latitude, `APPARENT='AIRLESS'`;
- `TIME_TYPE='UT'`, `TLIST_TYPE='JD'`, `CAL_FORMAT='JD'`, four public UTC epochs;
- `CSV_FORMAT='YES'` and `EXTRA_PREC='YES'` for unambiguous numeric parsing.

With permission to access the external service, from the repository root:

```bash
python -m pip install -r requirements-astronomy.txt
python scripts/fetch_horizons.py --fetch --strict --contact YOUR_CONTACT@example.com --output-dir horizons-audit-output
python scripts/fetch_horizons.py --from-archive horizons-audit-output --strict
```

The source is hard-coded to the official `https://ssd.jpl.nasa.gov/api/horizons.api` HTTPS endpoint. The downloader rejects wrong API signatures, target IDs, missing `ObsEcLon`, inconsistent Julian-day timestamps, mismatched observation counts, unparseable rows, unexpected redirects, and missing responses. It retains request URL and raw API body with SHA-256. The default strict difference tolerance is **30 arcseconds** (change explicitly with `--tolerance-arcsec`). Actual independent precision must be judged from the observed differences, not from the declared tolerance.

An archived file is **not NASA-signed**; re-opening it merely checks local integrity and numeric consistency. The manually triggered `.github/workflows/horizons-audit.yml` can be run after publication to perform the actual HTTPS fetch with a public, non-personal benchmark.

**Observed local status on 2026-11-20:** official Horizons fetch failed due to DNS resolution (`Temporary failure in name resolution`) in this cloud runtime. No authentic Moon or Pluto reference numeric table was obtained here. Synthetic unit tests validate parser/error behavior ONLY and MUST NOT be labeled a JPL cross-check. JPL Horizons does not provide astrological house cusps, so the independent geometry module closes a different verification obligation.

Official API: https://ssd-api.jpl.nasa.gov/doc/horizons.html ; official definition of quantity 31: https://ssd.jpl.nasa.gov/horizons/manual.html .


**v1.3.3-rc1 erratum:** The v1.3.2 default Swiss Pluto ↔ JPL 999 comparison had a target mismatch. Treat all earlier 999-vs-default-Swiss precision statements as exploratory rather than target-matched. See [JPL target verification](jpl-target-verification.md). Official direct source verification is still open.
