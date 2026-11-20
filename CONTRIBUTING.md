# Contributing

Thank you for improving symbolic-reflection-support. Contributions should make readings **more traceable, more honest about limitations, more useful, and more culturally respectful**.

## Local checks

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

## Pull request expectations

- Explain the behavior changed and include a repeatable example.
- Keep existing CLI commands and original output fields backward compatible unless proposing a major version.
- Add tests for Tarot/I Ching changes; for translation changes, include language-native review if feasible.
- Do not add deterministic examples falsely labeled as random casts.
- Respect privacy: no birth charts, names, identifiers, chat transcripts, or personal data in sample logs or issues without explicit, informed permission. Prefer fictitious test data.
- Distinguish script-verified facts, user-reported facts and symbolic interpretations.
- Attribute quotations and respect third-party copyright/licensing.
- Changes that add astrological or BaZi computation must document calendar, time zone, school conventions, independent verification cases and uncertainty.
- For safety-sensitive example prompts, use the [evaluation checklist](references/evaluation-checklist.md).

## Scope

This is a reusable Agent Skill, **not** a fortune teller or a clinical counseling tool. Please do not submit features that imply proven prediction, diagnosis, coercive relationship advice, or unbounded reassurance loops.

See [SECURITY.md](SECURITY.md) for responsible reporting.

## v1.2 catalog contributions

- `data/tarot.json`: preserve `rws-00`…`rws-77`, `names` and both `upright`/`reversed` cues in all six locales.
- `data/iching.json`: preserve King Wen number 1–64, the canonical Chinese names, pinyin and each locale's theme.
- Do not add classical quotations without edition/source verification and rights review. Treat these short prompts as *original symbolic material*, not predictions or evidence of psychological traits.
- For terminology updates, provide your preferred locale and explain why the wording is clearer, plus run the validator and unit tests. If you edit JSON catalog files, **regenerate `docs/index.html`'s embedded data using `python scripts/build_demo.py`** so it remains in sync. The website is intentionally single-file/offline.
- Test usability with users who do not already know Tarot or I Ching; avoid assuming a third party's feelings can be read from symbols.


## v1.3 astronomical contribution requirements

- Any new calendrical rule must cite an independently accessible reference, include a non-personal regression fixture and specify time zone, timescale, ephemeris and calendar school assumptions.
- Explicitly distinguish independent data references (e.g. HKO calendar dates) from numerical self-tests over the **same** astronomical model; do not label a Moshier fallback as an independent Swiss check.
- Do not add new astrological interpretations into deterministic output JSON or claim that computed chart data validates fortune telling.
- The v1.3 combined distribution uses **AGPL-3.0-or-later**. Check [`LICENSING.md`](LICENSING.md) before adding new dependencies or changing license notices.
