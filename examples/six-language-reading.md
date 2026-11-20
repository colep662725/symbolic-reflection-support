# v1.2 localized reading examples

Run a **real** one-card Tarot draw in Simplified Chinese:

```bash
python scripts/reflect.py tarot --count 1 --lang zh --json
```

Run three cards with optional reversals in Spanish:

```bash
python scripts/reflect.py tarot --count 3 --reversals --lang es
```

Decode **supplied** lines (not a cast) with Japanese themes:

```bash
python scripts/reflect.py iching --lines 7 8 7 9 7 8 --lang ja
```

This produces #49 革 with line 4 moving, resulting in #63 既济. The output must state `user_supplied_lines`; no coin toss was performed.

Look up one explicitly selected card and one hexagram in French and Portuguese:

```bash
python scripts/reflect.py card --id rws-15 --orientation reversed --lang fr
python scripts/reflect.py hexagram --number 63 --lang pt
```

For a deterministic, reproducible demonstration (not a new random act):

```bash
python scripts/reflect.py tarot --count 1 --seed 2026 --lang en --json
```

To experience a complete, offline, user-facing web UI, open `docs/index.html` directly in a modern browser. Do not conflate that browser run with Python output.
