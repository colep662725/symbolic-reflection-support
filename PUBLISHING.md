# Publishing & GitHub discovery checklist

The repository is **not** published merely by generating a ZIP. The repository owner must upload/commit these files and configure the GitHub metadata.

## Recommended GitHub metadata

**Repository name**

```text
symbolic-reflection-support
```

**Description** (copy this in GitHub → About → Edit):

```text
Multilingual Agent Skill: Tarot, I Ching, BaZi, solar terms and natal charts. Offline draws, verified calculations, six-language reflection.
```

**Topics** (add individually to GitHub → About → Edit):

```text
agent-skills
codex
tarot
i-ching
iching
astrology
self-reflection
multilingual
python
bazi
```

Choose topics that accurately describe the repository, and revisit them if the feature set changes. GitHub limits topics to 20, with lowercase letters/numbers/hyphens and up to 50 characters each. These labels are a recommendation, not already applied to any remote repository.

## Publication steps

1. Create a public `symbolic-reflection-support` repository on GitHub **if your account has publishing access**.
2. **License note:** v1.3+ changed the combined distribution from MIT to **AGPL-3.0-or-later** because of the optional Swiss Ephemeris integration. Review [`LICENSING.md`](LICENSING.md) before reusing or publicly hosting the computational extra.
3. Upload or commit the **contents** of the `symbolic-reflection-support/` folder to the repository root. Include `.github/workflows/ci.yml` and `LICENSE`.
4. Set the Description and Topics above. Add a website if there is a real project site; don't invent one.
5. Verify Actions → CI completes. If an optional external tool fails to run, don't claim the whole repository has been independently certified.
6. Tag a release such as `v1.3.5-rc2` and attach the distributable ZIP. Record changes in `CHANGELOG.md`.
7. On a fresh machine, check discovery and installation:

```bash
npx skills add OWNER/symbolic-reflection-support --list
npx skills add OWNER/symbolic-reflection-support --skill symbolic-reflection-support
```

8. **Optional live demo:** GitHub repository → Settings → Pages → Deploy from a branch → select your default branch and **`/docs`** folder. `docs/index.html` is self-contained and works as an online GitHub Pages site or as a local `file://` page. Do **not** advertise a Pages URL before it is deployed. When hosted, GitHub may log visits even though the demo includes no tracking.
9. Search on GitHub using `tarot agent skill`, `iching agent-skills`, `symbolic-reflection-support`, `topic:tarot`, and `in:readme` filters. Record whether the repository appears. Rankings and search indexing may take time and cannot be guaranteed.
10. If desired, share a **real, labeled** 15-30 second terminal capture of the command returning JSON; avoid implying random draws predict real events.

Official references:
- [Agent Skills specification](https://agentskills.io/specification)
- [Vercel Skills CLI commands](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)
- [GitHub: classifying your repository with topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics)
- [GitHub: searching for repositories](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories)

**Reality check:** GitHub README content is not part of the default repository search fields; name, description and topics matter most. Search `in:readme` explicitly when testing README matching. A public repository does not automatically appear in every third-party directory or make its software safe to install.

## v1.3.2 publication checks

- Run `python scripts/verify_ephemeris.py --strict`: this is **low-precision model** comparison only. Do not claim NASA DE440/Horizons high-precision certification.
- Run `python scripts/install_diagnostics.py --require-astronomy` and full Python tests.
- Have an actual Windows user run [the installation protocol](references/install-testing.md) and confirm Codex recognized `$symbolic-reflection-support`; do **not** substitute cloud CI for user acceptance.
- Keep all private birth profiles out of issue templates, examples and CI logs.

### Live JPL data is a separate opt-in validation

After publishing, use **Actions → Optional JPL Horizons Moon and Pluto barycenter/center audit → Run workflow**. It requests non-personal public epochs only, saves original JPL raw API responses and request URLs, and stores an artifact with the numerical comparison. This is not part of regular CI so a third-party service outage cannot be disguised as an ordinary unit-test failure.

**Do not claim the official JPL test passed until that workflow or a genuine Windows network run actually succeeds.** The local parser mocks and 144-cusp independent geometry checks are separate evidence.

## v1.3.4-rc1 acceptance gate

This is a release candidate, **not an official JPL certified release**. For the optional NASA manual Actions job, GitHub automatically supplies its actual repository URL in the `User-Agent` contact field. Check the JPL fair-use policy, ensure the repository URL is public, and preserve uploaded original response files and SHA256. See [official checklist](references/official-closure-checklist.md). Do not redistribute Swiss center-body binaries without separately reviewing their license.


## New Windows Python 3.13 compatibility check

The `.github/workflows/ci.yml` now includes a Windows Python 3.13 job that installs the `pysweph==2.10.3.6` binary wheel and runs all tests. This is declared as a *future CI requirement* until a real GitHub Actions log is available. Avoid advertising that CI has passed before the actual workflow runs.
