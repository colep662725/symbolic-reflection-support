# Security and privacy

## Local execution

`scripts/draw.py` uses the Python standard library only. Its purpose is to draw from an in-memory card list or produce/interpret six coin lines. It does not make network requests, read environment variables, fetch private files, send telemetry, or write persistent logs. Input is limited to CLI flags; no birth details are accepted by the script.

The optional `--seed` exists **only** for reproducible examples. The JSON SHA-256 fingerprint is a payload-consistency checksum, **not** cryptographic attestation of fair random sampling or protection against a malicious host.

## Reporting issues

For vulnerabilities, avoid posting sensitive personal details in a public issue. Contact the repository maintainer privately through their documented GitHub security contact, if available. If no private channel is configured, open an issue without any exploit secrets or private information and ask for a contact method.

No hosted service or bug-bounty program is promised by this repository. Third-party agents can execute skills with varying permissions; review scripts before installation and limit host permissions accordingly.

## Browser demo (v1.2)

`docs/index.html` is a self-contained HTML file. Its random draws use `crypto.getRandomValues()` with rejection sampling (not `Math.random`). It does not fetch external content, set cookies, store personal data or include analytics. If the browser does not provide Web Crypto, a draw should fail with an explanation rather than silently fall back to a weaker generator. Copying a JSON record is an explicit user action. Public hosting (e.g., GitHub Pages) may have separate infrastructure access logging.

Its bundled interpretations contain no clinical or supernatural certainty; the results do not warrant safety, medical, legal or financial decisions.


## Optional v1.3 astronomical calculation extra

`pyswisseph` is an external **AGPL-licensed** binary extension. `requirements-astronomy.txt` pins the tested package version. It is **not** bundled, and no Swiss ephemeris data files or natal user profiles are distributed. The Python modules calculate locally and output results to stdout; they do not transmit inputs, but shell history, clipboard, screenshots and CI consoles may retain them. Use neutral reference data in public issues and tests. Do not publish real users' private birth dates, times and coordinates without their explicit consent.

`--ephemeris swieph` may fall back to `moseph` if no Swiss data files are installed; `--strict-ephemeris` is offered to prevent unknowingly accepting that fallback. Never present a same-engine duplicate check as an independent scientific source.
