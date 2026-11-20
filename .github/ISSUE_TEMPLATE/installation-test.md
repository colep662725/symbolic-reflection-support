---
name: Windows installation test report
about: Report a clean user-side installation test without private birth data
labels: testing, installation
---

## Test environment (do not include user name, path, IP, or birth date)

- OS: Windows 10 / Windows 11 / other
- Python version:
- Skill version: 1.3.1
- Codex recognizes `$symbolic-reflection-support`: Yes / No / Not tested
- Optional astronomy dependency installed: Yes / No

## Evidence

- `scripts/windows-smoke-test.ps1` outcome: PASS / FAIL / Not run
- `scripts/install_diagnostics.py --require-astronomy` outcome: PASS / FAIL / Not run
- Test suite counts:
- What step failed, and what error **category** appeared? (redact full paths or private details)

## Important boundaries

Please do NOT attach real natal charts, date and place of birth, screenshots containing personal paths, API keys or private relationship/health information.

An actual Windows result is end-user feedback; a GitHub Actions success is **not** a substitute.
