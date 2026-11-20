# Horizons Moon 301 / Pluto system barycenter 9 / Pluto body center 999

**Version: v1.3.4-rc1 — source-consistent audit protocol, NOT an independently verified live Horizons data set.**

## Key target-definition correction

- `Moon` uses Horizons `COMMAND='301'`, geocenter `CENTER='500@399'` and Swiss `MOON`.
- The existing `natal.py` uses default Swiss Ephemeris `PLUTO`. The Swiss docs state normal planetary calculations refer to **system barycenters**, so its aligned JPL target is `COMMAND='9'` (Pluto-system barycenter), **NOT `999`**.
- `COMMAND='999'` is the physical Pluto body center. A separate official JPL 999 response can be paired with JPL 9 for **same-epoch angular center–barycenter offset**, including ecliptic latitude. Default Swiss PLUTO must not be relabeled as physical body center.
- To independently compare a Swiss body-center Pluto result to JPL 999, set `--compare-swiss-center` and supply the satellite ephemeris file `sepm9999.se1`, under an explicitly configured licensed Swiss Ephemeris path. The program selects Swiss target `9999` (not `swe.PLUTO` with `FLG_CENTER_BODY`) and fails instead of silently substituting the default barycenter.

References: [JPL Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html); [Horizons API docs](https://ssd-api.jpl.nasa.gov/doc/horizons.html); [Swiss Ephemeris documentation](https://www.astro.com/swisseph/swephprg.2.10.pdf).

## Official live audit (explicitly opt in to network)

```bash
python -m pip install -r requirements-astronomy.txt
python scripts/fetch_horizons.py --fetch --strict --contact https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY --targets Moon PlutoBarycenter PlutoCenter --output-dir horizons-audit-output
python scripts/fetch_horizons.py --from-archive horizons-audit-output --strict --targets Moon PlutoBarycenter PlutoCenter
```

Each HTTPS request returns Horizons observer `QUANTITIES='31'` (apparent ecliptic-of-date longitude and latitude), with `TIME_TYPE='UT'`, `TLIST_TYPE='JD'` and exact published test times. Outputs preserve the request URL, target ID, Earth (399) center header, raw JSON, source signature and SHA-256. Parsed values are compared with local Moshier for Moon 301 and Pluto barycenter 9. The two **official JPL** Pluto targets 9 and 999 are compared at precisely matching instants, with a **1 arcsecond test-sample separation threshold** using spherical angular distance. That threshold is not a universal physical bound.

An additional Swiss Pluto body-center numerical comparison is **not** part of the default audit because it requires a separate licensed satellite ephemeris dataset:

```bash
python scripts/fetch_horizons.py --fetch --strict --contact YOUR_CONTACT@example.com --compare-swiss-center \
  --swiss-ephe-path PATH_TO_SWISSEPH_EPHE_DIRECTORY \
  --targets Moon PlutoBarycenter PlutoCenter
```

**Never describe an archived GitHub value, synthetic fixture, or re-run of the Moshier library as an authenticated JPL Horizons HTTPS response.** The live source must actually be fetched. `--from-archive` checks numerical contents and file integrity but cannot reauthenticate the original TLS request.

## Current acceptance status

- Published third-party archive **attributed** to Horizons #31: 18 independent in-range timestamps for Moon and 18 for Pluto **barycenter** matched Moshier within the 30-arcsecond numerical regression threshold (the largest observed errors were approximately 1.774″ and 0.721″ respectively). This is a **secondary-attributed** numerical test, not official-source certification.
- Official JPL raw response: **unavailable in the current sandbox (DNS failed)** as of 2026-11-20. The official direct-fetched audit is **OPEN**.
- Independent JPL Pluto 9 versus 999 numeric same-epoch comparison: **OPEN** until both original official responses are obtained. The identity mapping and separate validation **protocol** are established.
- Swiss Pluto body-center direct matching: **OPEN** because the file `sepm9999.se1` is not present in the current sandbox and is not bundled in this repository.

No conclusions about fate prediction, personality or subjective experience follow from astronomical coordinates.

See [complete official acceptance checklist](official-closure-checklist.md) for reproducible details and the explicit open/closed matrix.
