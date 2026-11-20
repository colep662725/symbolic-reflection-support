# Reproducible BaZi calendar example (non-personal test input)

The day-cycle and month rules can be checked against the HKO 60-stem table and a public almanac, without using someone's personal birth data.

```bash
python -m pip install -r requirements-astronomy.txt
python scripts/bazi.py --datetime 2024-02-10T12:00:00 --tz Asia/Shanghai --lat 39.9042 --lon 116.4074 --compare-boundaries
```

Expected: year `甲辰`, month `丙寅`, day `甲辰`, hour `庚午`; `predictions_supported` is false. The result includes UTC, local timezone, four-character pillar data and the effective model. For a 23:xx birth, use `--compare-boundaries` to see the **different late-Zi rules**, and use `--clock apparent-solar` only if that convention was explicitly chosen. No identity/sex or fortune should be inferred.

`--direction forward|backward` returns conventional ten-year cyclical stems and an **approximate** start age. The `--traditional-sex` option is not required when direction is supplied explicitly.
