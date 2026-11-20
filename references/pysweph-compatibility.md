# `pyswisseph` and `pysweph`: validated wrapper compatibility

The **same** `import swisseph as swe` may resolve to different Python bindings.
Legacy `pyswisseph==2.10.3.2` has 2-element `calc_ut()` and 12-element `houses_ex()` cusps.
Modern `pysweph==2.10.3.6` exposes a 3-element `calc_ut()` tuple `(positions, flags, diagnostic)` and 13-element cusp tuples with a **dummy index 0**. `deltat_ex()` adds a diagnostic element. The C ephemeris version may still say `2.10.03` in both; it is **not** a reliable Python distribution identifier.

All project callers use `scripts/swiss_compat.py` to normalize these interfaces. Installation diagnostics report the Python distribution and its version. Both installed at once is an error, because they provide the same import name. Changing the wrapper never changes the requested ephemeris target or permits fallback to a different target.

`requirements-astronomy.txt` selects `pysweph==2.10.3.6` for Python 3.13+, which has a Windows x86-64 binary wheel, and legacy `pyswisseph==2.10.3.2` below Python 3.13. The user must install dependencies using the same Python interpreter used to run the skill (typically `py -3` on Windows). No C++ build tools should be necessary for this supported Windows 3.13 wheel.

## Tests / limits

- Real local tests use the installed `pyswisseph` binding to reproduce legacy calculations.
- Additional integration tests use an **ABI simulation proxy** to reproduce modern 3-return-value calculations and 13-cusp arrays. This is not equivalent to executing an actual `pysweph` wheel on Windows.
- For definitive cross-platform acceptance, run the `windows-smoke-test.ps1` and `windows-jpl-audit.ps1` scripts on the real Windows 3.13 machine and keep their logs.
- The user reported successful Moon / Pluto barycenter / Pluto body-center Swiss flag tests on their Windows machine. That is evidence of **local calculation success**, not yet a NASA/Horizons independent numerical comparison.

Upstream docs: <https://github.com/sailorfe/pysweph/blob/pysweph/docs/concepts/migration_guide.md>.
