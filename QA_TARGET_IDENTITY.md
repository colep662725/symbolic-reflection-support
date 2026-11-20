> **v1.3.5-rc1 update:** Windows user reported successful real Swiss `9999` calculation (alongside Moon and Pluto barycenter) with separate `sat/sepm9999.se1`; NASA raw-response comparison remains open. The new cross-version compatibility layer supports modern `pysweph` responses. This is a report of user-side success, not independently reproduced on this Linux runner.

# JPL / Swiss target identity audit — v1.3.4-rc1

**2026-11-20. Status: correct target-ID and fail-closed code validated; live NASA/JPL direct-data authentication and physical Pluto body-center numerical check remain OPEN.**

## Verified target identities

| Role | Horizons (geocentric observation target) | Swiss Ephemeris (pyswisseph) | Live verification status |
|---|---|---|---|
| Moon physical center | 301 | `swe.MOON` | Not yet directly fetched from JPL in this environment |
| Pluto system barycenter | 9 | `swe.PLUTO` (default) | Public third-party-attributed archive numerically crosschecked; direct JPL open |
| Pluto physical center | 999 | **9999** (Swiss separate satellite object ID) | Independent Swiss file and direct JPL response missing |

In v1.3.2, the default Swiss `PLUTO` was mismatched to JPL `999`. In v1.3.3-rc1, the standard `PLUTO` vs JPL `9` mapping was corrected, but an optional Swiss **body-center implementation incorrectly used the `FLG_CENTER_BODY` flag on `PLUTO`**. Both issues are now addressed: v1.3.4-rc1 uses target 9999, which Swiss Ephemeris v2.10 defines as Pluto's body center, *not* a flag on the default planet object. Actual Swiss target `9999` calculation requires independently licensed `sat/sepm9999.se1` and sufficient additional ephemeris support.

## Measured and unmeasured results

- **Measured in previous local runs:** 18 in-range published secondary JPL-attributed epochs for Moon and 18 for Pluto system barycenter satisfied the predeclared 30 arcsecond numeric threshold. This is **not** live provenance or proof of NASA issuance.
- **Measured this release:** `swe.calc_ut(2451545.0, 9999, swe.FLG_SWIEPH | swe.FLG_SPEED)` fails with: `sepm9999.se1 not found`. This is a genuine missing-data result, not a successful center computation.
- **Not measured:** any actual JPL `9` vs `999` same-epoch pair obtained directly from an official live HTTPS response in the present workspace.
- **Not measured:** Swiss target `9999` with an actually installed official satellite ephemeris file matched numerically to JPL `999`.

## Hardened tests and provenance handling

New code verifies correct ID 9999, disallows `FLG_CENTER_BODY` substitutions, checks `FLG_SWIEPH` on returned center positions, checks for a nontrivial `sat/sepm9999.se1`, preserves failure manifests on partial live fetch, validates API source and object headers, preserves the precise query and raw-response digest, and records any missing-origin evidence as unverified.

JPL requests now use an explicit contact email or published HTTPS project URL in the User-Agent to comply with the [JPL API fair-use policy](https://ssd-api.jpl.nasa.gov/). Code retries only transient HTTP failures, not DNS failures, and accesses one target at a time.

## Reproduction

See [official closure checklist](references/official-closure-checklist.md) for the exact commands, files, user-consent requirements, acceptance criteria, and limitations.

Primary sources:
- https://www.astro.com/swisseph/swephprg.htm (Swiss 9999 and sat folder)
- https://ssd-api.jpl.nasa.gov/doc/horizons.html (Horizons official API)
- https://ssd.jpl.nasa.gov/horizons/manual.html (observer #31 and coordinates)

**Neither numerical ephemeris agreement nor a symbolic reading is evidence of predictive power about a person's life.**
