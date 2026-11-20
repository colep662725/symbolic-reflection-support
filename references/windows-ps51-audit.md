# Windows PowerShell 5.1: real ephemeris acceptance, UTF-8, and hash scopes

## What was actually observed (2026-11-20)

The user ran Swiss `9999` on Windows Python 3.13 and returned four finite positions with Swiss-file engine confirmation; their official NASA/JPL HTTPS audit console then reported 12/12 matched-target comparisons (Moon 301, Pluto barycenter 9, Pluto body center 999) and four paired 9-vs-999 angular separations. The reported maximum in that finite sample was 0.09118717 arcsec. The conversation includes the console report, **not** the three saved original HTTP responses. This repo cannot independently certify the authenticity of those private files.

## Why `Get-FileHash` differed from `manifest.raw_sha256`

The old manifest field `raw_sha256` is calculated over the original NASA HTTP response `buf`, before it is embedded in an outer JSON document. The saved file `horizons_moon_public.json` is a larger JSON object with a `raw_api_response` string and metadata. Its file SHA-256 **must be different** from the raw response digest in general. This is not itself evidence of corruption.

- `raw_sha256`: SHA-256 of **raw HTTP response bytes**.
- `raw_api_sha256` inside the saved JSON: same raw-response scope.
- `archived_json_sha256` (new): SHA-256 of **the entire saved JSON wrapper bytes**, including metadata.

Run with no network:

```powershell
cd "$env:USERPROFILE\.codex\skills\symbolic-reflection-support"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
py -3 scripts/check_horizons_hashes.py --archive .horizons-audit
```

For a legacy archive, `PASS_RAW_ONLY_LEGACY` means all recorded **raw-response** hashes agree but the old manifest does not contain a **whole-file** expected hash. It does **not** mean a new NASA call has occurred or that the original HTTPS source has been reauthenticated.

If you need a future audit to commit both scopes, perform a new, explicitly authorized live audit. New archives include `archived_json_sha256` and emit `PASS_BOTH_HASH_SCOPES` after local verification. Re-downloading is not required merely to establish that the earlier hashes referred to different byte sequences.

## Fixing Windows 3.13 return shapes and text output

- `pysweph` may return `(position, flags, diagnostic)` instead of two objects.
- `houses_ex` may return 13 cusps (index zero unused) instead of 12.
- `deltat_ex` may return `(value, diagnostic)` instead of scalar.
- Test mocks/proxies must accept both real installed ABIs before synthesizing the modern shape.
- Locales using a Windows OEM code page may fail to serialize French/Portuguese/Spanish output; reflection CLI explicitly configures UTF-8, and unit tests decode UTF-8. In legacy PowerShell, set `PYTHONIOENCODING=utf-8` when displaying multilingual output.
- File path matching must tolerate both `/` and `\`.

Run full tests:

```powershell
py -3 -m unittest discover -s tests -v
```

No personal birth times, JPL contact details, authenticated browser cookies, or Swiss licensed binary ephemerides are in the GitHub bundle.
