# Windows / Codex: genuine end-user acceptance protocol

**Developer Linux tests are not real Windows user installation tests.** The goal is for a separate human user to install the published ZIP on Windows 10/11, then run an opt-in diagnostic on their computer.

## Install and test (PowerShell)

1. Unzip `symbolic-reflection-support-v1.3.5-rc1.zip` under `%USERPROFILE%\.codex\skills`, so that `%USERPROFILE%\.codex\skills\symbolic-reflection-support\SKILL.md` exists.
2. Install Python 3.10+ with `venv` and accessible `python` or `py` launcher.
3. Open PowerShell in the extracted `symbolic-reflection-support` directory and, **only if willing to allow pinned `pip` downloads**, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows-smoke-test.ps1 -CheckCodexInstalled
```

`windows-smoke-test.ps1` creates a private temporary virtual environment, invokes `pip install -r requirements-astronomy.txt`, validates metadata and local web demo parity, runs public sample Tarot, I Ching, BaZi and natal examples, checks the independent lower-precision ephemeris implementation and runs repository tests. It generates an installation JSON report locally; it does not phone home.

Run without `-CheckCodexInstalled` if testing a GitHub source checkout outside the actual installed Codex path. With `-SkipInstall`, the isolated venv deliberately has no astronomy extra, so strict checks will fail: this is useful for testing *missing dependency* errors, not a pass condition.

If PowerShell blocks scripts due to policy, review the script before executing. No administrator rights should be needed. For teams, use your organization's approved package source and security process.

## Pass conditions

1. Python interpreter, IANA timezone database and pinned Swiss dependency are available.
2. Skill metadata and catalogs validate; source-to-browser catalog consistency checks pass.
3. Both deterministic and nonrandom user-supplied commands execute correctly, including `7 8 7 9 7 8` becoming `革 → 既济`.
4. Public example BaZi and natal scripts exit 0 with valid JSON. They should not request personal birth data.
5. Independent approximate ephemeris benchmark passes all 66 threshold checks.
6. Full unittest suite passes in Windows venv. Separately confirm that **Codex actually discovers** `$symbolic-reflection-support` and that a short daily-reading request leads to a script run, not an invented card.

## Evidence, privacy and failure handling

`install_diagnostics.py` deliberately omits personal names, precise paths, hostname, IP and birth data. Before sharing an installation report, **review it yourself**; tool execution failures should be reported without publicly posting personal information. If reporting a failure, include OS family, Python version, step that failed, command exit code and whether the optional dependency was installed. Never upload natal JSON with real names/birth data to GitHub.

## Still unverified until a real user runs it

Passing these tests on the model's Linux host is a simulated, not an observed end-user Windows installation. A real tester should provide an explicit Windows pass/fail report plus a separate confirmation that the Codex Skill can be invoked. Do not automatically count the CI Windows matrix as an end-user installation test.


### Windows Python 3.13 user-verified troubleshooting

If `pyswisseph` tried to build from source and demanded MSVC, use the v1.3.5 `requirements-astronomy.txt` in the same Python 3.13 interpreter: `py -3 -m pip install --only-binary=:all: -r requirements-astronomy.txt`. It chooses `pysweph`, which exports the *same* `swisseph` import but a different ABI. The compatibility module normalizes this. The user previously reported Moon/Pluto barycenter/Pluto center 9999 all PASS with their Swiss data files; the current ZIP has not yet completed a real user-host full regression. To audit JPL, use `scripts/windows-jpl-audit.ps1` explicitly.
