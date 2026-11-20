# 24 solar terms and calendar cross-checks

```bash
python scripts/solar_terms.py --year 2024 --tz Asia/Shanghai --verify-bisection
```

Yields 24 entries from **2024 立春 through 2025 大寒**. Each entry has an explicit target apparent Sun longitude, UTC and Asia/Shanghai local date-time, and a numerical self-check. The 22 local dates within February–December 2024 match the independent Hong Kong Observatory [2024 calendar](https://www.hko.gov.hk/tc/gts/time/calendar/pdf/files/2024.pdf). This is **date-level cross-checking only**. Independent ephemeris comparison at minute or arcsecond resolution is not asserted.
