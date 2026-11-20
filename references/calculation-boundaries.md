# Astrology, BaZi and calendar calculation boundaries

**Since v1.3, the optional [astronomy calculation modules](astronomy-computation.md) calculate a tropical natal chart, 24 solar-term crossings, BaZi four pillars and conventional ten-year luck-cycle arithmetic using pinned `pyswisseph`.** The offline Tarot/I Ching core remains standard-library-only; the v1.2 demo does not perform astronomy. No Swiss ephemeris data files are bundled. Avoid confusing computed astronomical/calendar outputs with the unverified interpretive meanings of those outputs.

## Western birth charts

- Prefer an existing chart supplied by the user. State whether a number was provided by the user, computed by a verified tool, or assumed for an illustration.
- For a requested calculation, obtain **date, local birth time, place**, time zone including historically relevant DST, zodiac type (tropical or sidereal) and house system. Prefer local computation; if sharing birth data with a third party is necessary, ask before disclosing.
- If birth time is approximate, explicitly discuss sensitive positions (especially Ascendant and houses). Do not infer a precise birth time from personality traits.
- If no verifiable ephemeris/calculator is available, interpret only already verified placements. Do **not** fabricate exact degrees, houses, aspects or transits.
- Astrological periods and named cycles can be discussed as **traditional symbolic frameworks**, not evidential life-event forecasts.

## BaZi / 四柱八字

- Confirm the **Gregorian birth date, local clock time, location, historically correct time zone and solar-term boundary convention**.
- Late-night birth in the Zi hour (23:00–00:59) may produce different day/time pillars under **子初换日 vs 午夜换日**, and there are school differences concerning late-Zi hour stem treatment. Show alternatives when the result genuinely depends on that choice; do not blend two charts into one.
- Month pillars normally depend on **jie (节) solar terms**, not simply Gregorian month numbers or lunar month labels.
- Traditional ten-year luck-cycle direction depends on school-specific conventions and may ask for a male/female parameter. Do not assume this from the user's name or history. Give transparent alternatives when that parameter is missing.
- Start-of-luck calculations require a verified precise birth time and the relevant solar-term timestamp, plus an explicit conversion convention. If those are not available, do not invent an exact start date or year.
- Separately identify each assumption used for 日主、十神、五行、格局、起运. Don't claim one school as universally authoritative.

## Zi Wei Dou Shu, numerology and related traditions

- Specify which school, calendar and calculation conventions are used. For numerology, display the arithmetic and the reduction convention, including whether master numbers are preserved.
- Do not claim a user has a fixed destiny, can diagnose a disease, or can infer an unconsenting third party's behavior from a chart.
- Predictions about marriage, money, death, health or other consequential events are not verifiable from these methods. Translate them into user-directed reflection topics and practical planning, with appropriate caveats.

## Format for any computed chart

1. **User-provided inputs:** precise or approximate; what remains missing.
2. **Computational method:** tool/source, timezone, rule choices and calculation date where relevant.
3. **Verified outputs:** positions or pillars with explicit uncertainty.
4. **Symbolic interpretation:** in terms of possible questions, not proven traits or outcomes.
5. **Reality checks:** what observations could support/refute the practical hypothesis.

Never represent general astrological symbols as empirically validated personality or predictive mechanisms.
