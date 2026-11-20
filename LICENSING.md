# Licensing of v1.3.x (including v1.3.1) — please read before publishing

**Important breaking change:** v1.2.0 was published as MIT. **This v1.3.x combined distribution is offered under GNU AGPL-3.0-or-later** to comply with the Swiss Ephemeris Python integration. The unmodified v1.2.0 release and its MIT grant remain available and unaffected. The earlier MIT notice is preserved in [`LICENSE.MIT-v1.2`](LICENSE.MIT-v1.2).

- The **new `bazi.py`, `solar_terms.py`, `natal.py` and `calendar_core.py`** call `pyswisseph`/Swiss Ephemeris. `pyswisseph` is licensed under AGPL-3.0; Swiss Ephemeris offers AGPL or a separately negotiated commercial Professional License.
- The repository **does not bundle** third-party binaries, precomputed Swiss ephemeris files, keys, JPL ephemerides, or personal birth records. The optional dependency is installed separately using [`requirements-astronomy.txt`](requirements-astronomy.txt).
- If you redistribute or publicly host a service based on the v1.3 integration, **review and comply with the AGPL**, including applicable corresponding-source/network obligations. A commercial Swiss Ephemeris license might be an alternative; this package has *not* purchased one.
- Third-party terms apply independently. The project includes its own copyright and complete AGPL text in [`LICENSE`](LICENSE).
- These are licensing implementation choices, not legal advice. **Do not call the v1.3 repository MIT** without removing/replacing the Swiss integration and resolving the required license obligations.

Sources: [Swiss Ephemeris licensing](https://www.astro.com/swisseph/swephprg.pdf), [pyswisseph upstream README](https://github.com/astrorigin/pyswisseph/blob/master/README.rst), [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html).

## Extra satellite ephemerides

The optional Swiss physical Pluto body center target `9999` requires separately obtained `sat/sepm9999.se1` and any necessary standard Swiss ephemeris files. **No third-party satellite or JPL binary is redistributed in either ZIP.** Obtain and use them under their applicable Astrodienst/Swiss licensing terms; refer to https://www.astro.com/ftp/swisseph/ephe/sat/ .


## Python 3.13 binding alternative

The optional `pysweph==2.10.3.6` is a community-maintained continuation of the AGPL Swiss Ephemeris bindings. Its `import swisseph` API has a different Python return ABI. This project normalizes the interface and retains the AGPL distribution obligations. The proprietary Swiss Professional License option requires direct agreement and is not automatically granted by use of the package.
