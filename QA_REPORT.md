# QA Report — symbolic-reflection-support v1.3.5-rc2

## Explicit scope

- Fixed Windows PowerShell 5.1 UTF-8 subprocess failures, Win32 path regex, and modern Swiss ABI test double.
- Added independent stdlib-only archive integrity checker, preserving v1.3.5-rc1 legacy manifests.
- Reported JPL live HTTP success originates in **user Windows console log**, and original NASA raw responses were not uploaded into or bundled with this release candidate.
- No astronomy formulas or traditional interpretation tables were changed.

## Tests

See the separately generated QA file and test log in this turn for the actual local test counts. Native Windows 3.13 `pysweph` full-suite rerun remains pending user acceptance; Linux tests do not substitute for that test.

# QA Report — Symbolic Reflection Support v1.3.5-rc1

**Report date: 2026-11-20. Classification: release candidate, NOT an officially JPL-certified astronomy release.**

## Change and evidence summary

The Windows user reported three successful local Swiss calculations: Moon, default Pluto barycenter, and physical Pluto body center `9999`, with `sepl_18.se1`, `semo_18.se1`, `sat/sepm9999.se1` present. This closes the earlier **unable-to-run** blocker on the user's PC, but the calculation log was not uploaded with the new build, and no independent Horizons result was obtained in this build environment.

A new `scripts/swiss_compat.py` normalizes:

| API | `pyswisseph==2.10.3.2` | `pysweph==2.10.3.6` |
|---|---|---|
| `calc_ut` | `(positions, flags)` | `(positions, flags, message)` |
| `houses_ex` | 12 cusps | 13 cusps; index 0 unused |
| `deltat_ex` | number | `(number, message)` |

`requirements-astronomy.txt` selects a distribution based on the Python version. Python 3.13 uses the precompiled `pysweph` wheel rather than attempting to compile the original package. GitHub CI now contains a real modern-Windows-wheel test job, **not executed here**.

### Local tests actually executed

- `python -m unittest discover -s tests -q`: **111/111 pass** (33.276 seconds in the source tree; 33.478 seconds after clean installer ZIP extraction). Includes synthetic modern-ABI proxy integration and real legacy `pyswisseph` calculations.
- `python scripts/validate_skill.py`: pass (internal sanity check, **not** `skills-ref validate`).
- `python scripts/build_demo.py --check`: pass.
- Both GitHub Actions YAML workflows parse as valid YAML locally; no remote Actions run has been performed.
- `python scripts/verify_ephemeris.py --strict`: 66/66 independent **approximate-model** comparisons pass. Not JPL high-precision validation.
- `python scripts/verify_placidus.py --strict`: 144/144 independent geometrical comparisons pass for documented public moderate-latitude cases. Largest observed difference ~0.430234 arcsec; does not cover extreme polar charts.
- `python scripts/install_diagnostics.py --require-astronomy`: 9/9 pass in the local **Linux** test environment with legacy `pyswisseph` 2.10.3.2.

### NASA/JPL official status (still OPEN)

- Official Horizons API host: `https://ssd.jpl.nasa.gov/api/horizons.api`, Earth center `500@399`.
- Observer quantity `31`, apparent geocentric ecliptic longitude/latitude, exact public UTC epochs.
- Target `301` Moon, `9` Pluto-system barycenter, `999` Pluto physical body center. Local Swiss physical center uses *different* target number `9999`.
- This container's direct DNS probe failed to resolve `ssd.jpl.nasa.gov`. See `evidence/jpl-network-attempt-v135.json`. No official `$$SOE...$$EOE` original response was received; no numerical JPL `9↔999` offset was computed in this run.
- `scripts/windows-jpl-audit.ps1` is designed to run on the Windows PC where all three Swiss calculations previously succeeded, explicitly prompts for contact, and executes strict official GET and archive verification with Swiss file engine `swieph`. It records raw source responses, SHA-256, requests, mismatches, and failure manifest.
- The JPL parser has mock-contract tests, **not** a successful live NASA payload test on this release.

**Do not label this version as JPL DE440/DE441 validated until a live audit completes** and the manifest shows all three target comparisons passing.

### Installation and privacy

The project ZIP does not bundle third-party `sepm9999.se1`, personal birth dates, or NASA raw responses. No user records are transmitted. Official requests use only four public neutral test instants. Full Windows 3.13 + `pysweph` wheel and real user-host skill invocation must be tested after installation of this ZIP.

The Swiss Ephemeris runtime and this integrated software remain subject to the distribution's AGPL or separately licensed commercial conditions. Astronomical calculations are not scientific predictions of fate, relationships, or health.
