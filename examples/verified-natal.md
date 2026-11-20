# Reproducible Western natal astronomy example (neutral benchmark)

```bash
python -m pip install -r requirements-astronomy.txt
python scripts/natal.py --datetime 2000-01-01T12:00:00 --tz Europe/London --lat 51.4779 --lon 0 --houses placidus --cross-check --uncertainty-minutes 15
```

The JSON includes ten bodies' apparent ecliptic longitudes, ASC, MC, Placidus cusps, house membership by **ecliptic longitude** and `effective_ephemeris`. Without Swiss `.se1` files, the `swieph` request typically **falls back to Moshier**; the script labels a double-Moshier cross-check `NOT_INDEPENDENT`. It does not fabricate a second independent chart or infer a destiny.

Whole-sign example: replace `--houses placidus` with `--houses whole-sign`. Never silently replace Placidus at polar latitudes; handle an error explicitly. Any output from the ephemeris is astronomy; further personality or life-event interpretations are symbolic traditions.
