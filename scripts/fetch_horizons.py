#!/usr/bin/env python3
"""Opt-in NASA/JPL Horizons audit (v1.3.5-rc2; observational astronomy only).

The default Swiss Ephemeris PLUTO target is the *Pluto-system barycenter*:
  Swiss PLUTO     <-> Horizons COMMAND=9
  Swiss MOON      <-> Horizons COMMAND=301
  Horizons 999    = Pluto *body center*; Swiss uses separate target ID 9999
                    and the non-bundled sat/sepm9999.se1 file. Never relabel
                    Swiss PLUTO (9) with a CENTER_BODY flag.

No network fetch happens unless --fetch is provided. No personal data is
collected. The official host and TLS origin are recorded with exact request
URLs and raw response hashes. Archived data cannot prove TLS provenance.

Docs: https://ssd-api.jpl.nasa.gov/doc/horizons.html
      https://ssd.jpl.nasa.gov/horizons/manual.html
      https://www.astro.com/swisseph/swephprg.2.10.pdf
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ephemeris_reference import angular_distance, jd_from_utc
from calendar_core import calc_planet, require_engine, actual_engine
from swiss_compat import calc_ut as compat_calc_ut, installed_binding

HORIZONS_URL = 'https://ssd.jpl.nasa.gov/api/horizons.api'
VERSION = '1.3.5-rc2'
SWISS_PLUTO_BODY_CENTER_ID = 9999
SWISS_PLUTO_CENTER_FILENAME = 'sepm9999.se1'
PUBLIC_EPOCHS = (
    '2000-01-01T12:00:00+00:00',
    '2010-08-15T09:00:00+00:00',
    '2024-06-21T00:00:00+00:00',
    '2026-11-20T00:00:00+00:00',
)
TARGETS = {
    'Moon': {'horizons_id': 301, 'role': 'body_center', 'swiss': 'MOON'},
    'PlutoBarycenter': {'horizons_id': 9, 'role': 'system_barycenter', 'swiss': 'PLUTO'},
    'PlutoCenter': {'horizons_id': 999, 'role': 'body_center', 'swiss': None},
}
DEFAULT_TARGETS = ('Moon', 'PlutoBarycenter', 'PlutoCenter')
CSVFLOAT = re.compile(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?\Z')


def normalize_targets(names) -> tuple[str, ...]:
    names = tuple(names)
    if len(names) != len(set(names)):
        raise ValueError('Repeated audit target')
    if not names or any(x not in TARGETS for x in names):
        raise ValueError('Audit target must be one of: ' + ', '.join(TARGETS))
    return names


def build_official_url(target: str, epochs: tuple[str, ...] = PUBLIC_EPOCHS) -> tuple[str, list[float]]:
    if target not in TARGETS:
        raise ValueError('Unknown Horizons target; use an explicit target name')
    jds = []
    for iso in epochs:
        dt = datetime.fromisoformat(iso)
        if dt.utcoffset() is None:
            raise ValueError('UTC epoch must include explicit timezone offset')
        jds.append(round(jd_from_utc(dt.astimezone(timezone.utc)), 9))
    if not 1 <= len(jds) <= 20:
        raise ValueError('Use between 1 and 20 public test epochs')
    params = {
        'format': 'json',
        'COMMAND': f"'{TARGETS[target]['horizons_id']}'",
        'OBJ_DATA': "'YES'", 'MAKE_EPHEM': "'YES'", 'EPHEM_TYPE': "'OBSERVER'",
        'CENTER': "'500@399'", 'TLIST': ','.join(f"'{x:.9f}'" for x in jds),
        'TLIST_TYPE': "'JD'", 'TIME_TYPE': "'UT'", 'CAL_FORMAT': "'JD'",
        'QUANTITIES': "'31'", 'ANG_FORMAT': "'DEG'", 'APPARENT': "'AIRLESS'",
        'CSV_FORMAT': "'YES'", 'EXTRA_PREC': "'YES'", 'REF_SYSTEM': "'ICRF'",
        'SKIP_DAYLT': "'NO'",
    }
    return HORIZONS_URL + '?' + urlencode(params), jds


def validate_contact(contact: str) -> str:
    """JPL fair-use requires an application-specific contact address or URL.

    This is not a birth-data field. The caller explicitly opts in to networking.
    """
    if not isinstance(contact, str) or len(contact) > 180 or not contact.isascii() \
            or any(x in contact for x in ('\r', '\n', ' ', '\t')):
        raise ValueError('Provide --contact EMAIL or HTTPS project URL for JPL fair use')
    email = re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', contact)
    url = urlsplit(contact)
    public_https_url = url.scheme == 'https' and bool(url.netloc) and not url.username
    if not (email or public_https_url):
        raise ValueError('Provide --contact EMAIL or HTTPS project URL for JPL fair use')
    return contact


def verify_center_ephemeris_directory(path: Path) -> Path:
    """Require independently obtained licensed satellite ephemeris file.

    Swiss expects `sat/` under its ephemeris root. Never bundle the binary.
    """
    root = path.expanduser().resolve()
    f = root / 'sat' / SWISS_PLUTO_CENTER_FILENAME
    if not f.is_file() or f.stat().st_size < 1024:
        raise FileNotFoundError(
            f'Missing licensed Swiss Pluto body center file: {f}. '
            'Download it separately from official Astrodienst Swiss Ephemeris sat directory; '
            'do not supply or substitute a barycenter result.'
        )
    return root


def parse_horizons_payload(payload: str, target: str, expected_jds: list[float]) -> dict:
    if target not in TARGETS:
        raise ValueError('Unknown target')
    envelope = json.loads(payload)
    if not isinstance(envelope, dict):
        raise ValueError('Expected an API JSON object')
    signature = envelope.get('signature')
    if not isinstance(signature, dict) or 'NASA/JPL Horizons' not in str(signature.get('source', '')):
        raise ValueError('Response not labeled NASA/JPL Horizons API')
    if envelope.get('error'):
        raise ValueError('Official Horizons response contains API error: ' + str(envelope['error'])[:200])
    raw = envelope.get('result')
    if not isinstance(raw, str) or '$$SOE' not in raw or '$$EOE' not in raw:
        raise ValueError('Missing Horizons $$SOE / $$EOE table')
    if 'ObsEcLon' not in raw or 'ObsEcLat' not in raw:
        raise ValueError('Missing Horizons observer quantity #31 header')
    if re.search(r'(?i)error(?:\s+message)?\s*:', raw):
        raise ValueError('Horizons body contains error diagnostic')
    match = re.search(r'(?mi)^Target body name:\s*[^\r\n]*\((\d+)\)', raw)
    if not match or int(match.group(1)) != TARGETS[target]['horizons_id']:
        raise ValueError('target body header ID does not match requested Horizons target')
    if not re.search(r'(?mi)^Center body name:\s*Earth\s*\(399\)', raw):
        raise ValueError('Missing geocentric Earth (399) center header')
    block = raw.split('$$SOE', 1)[1].split('$$EOE', 1)[0]
    rows = []
    for line in block.splitlines():
        if not line.strip():
            continue
        fields = [x.strip() for x in next(csv.reader([line]))]
        if not fields or not CSVFLOAT.fullmatch(fields[0]):
            raise ValueError('Expected Horizons CSV with JD as first field')
        j = float(fields[0])
        floats = [float(x) for x in fields[1:] if CSVFLOAT.fullmatch(x)]
        if len(floats) != 2:
            raise ValueError(f'Quantity 31 must have exactly 2 numeric fields, found {len(floats)}')
        lon, lat = floats
        if not (math.isfinite(j) and math.isfinite(lon) and math.isfinite(lat)
                and 0 <= lon < 360 and -90 <= lat <= 90):
            raise ValueError('Non-finite or out-of-range Horizons quantity #31')
        rows.append({'julian_day_ut': j, 'longitude_deg': lon, 'latitude_deg': lat})
    if len(rows) != len(expected_jds):
        raise ValueError(f'Expected {len(expected_jds)} rows; found {len(rows)}')
    for k, (obs, expected) in enumerate(zip(rows, expected_jds)):
        if abs(obs['julian_day_ut'] - expected) > 1 / 864000:
            raise ValueError(f'timestamp mismatch at row {k}')
    return {'signature': signature, 'observations': rows, 'raw_result': raw}


def check_swiss_body_center(ephe_root: Path, epochs: tuple[str, ...] = PUBLIC_EPOCHS) -> dict:
    """Offline diagnostic: Swiss 9999 is *not* independent Horizons evidence."""
    swe = require_engine()
    root = verify_center_ephemeris_directory(ephe_root)
    swe.set_ephe_path(str(root))
    f = root / 'sat' / SWISS_PLUTO_CENTER_FILENAME
    results = []
    for stamp in epochs:
        jd = jd_from_utc(datetime.fromisoformat(stamp).astimezone(timezone.utc))
        try:
            data, flags, diag = compat_calc_ut(swe, jd, SWISS_PLUTO_BODY_CENTER_ID,
                                      swe.FLG_SWIEPH | swe.FLG_SPEED)
        except Exception as exc:
            raise RuntimeError('Swiss 9999 center calculation failed; satellite/planet files '
                               'or the supported date range may be missing: ' + str(exc)) from exc
        if not flags & swe.FLG_SWIEPH:
            raise RuntimeError('Swiss 9999 did not use Swiss ephemeris files; no silent Moshier fallback')
        results.append({'utc': stamp, 'center_longitude_deg': round(data[0] % 360, 9),
                        'center_latitude_deg': round(data[1], 9), 'target': 9999, 'engine_diagnostic': diag})
    return {'schema_version': VERSION, 'status': 'PASS_SWISS_9999_LOCAL_ONLY',
            'ephemeris_file': SWISS_PLUTO_CENTER_FILENAME,
            'file_size_bytes': f.stat().st_size,
            'file_sha256': hashlib.sha256(f.read_bytes()).hexdigest(),
            'engine': 'Swiss Ephemeris satellite data (9999)',
            'observations': results,
            'official_jpl_provenance': False,
            'note': 'Successful local center positions alone do not certify comparison to NASA Horizons 999.'}


def compare_external(target: str, epochs: tuple[str, ...], reference: dict,
                     tolerance_arcsec: float, compare_swiss_center: bool = False,
                     swiss_engine: str = 'moseph') -> dict:
    if not 0 < tolerance_arcsec <= 3600:
        raise ValueError('Tolerance must be in (0,3600] arcsec')
    if target == 'PlutoCenter' and not compare_swiss_center:
        return {'target': target, 'target_id': 999, 'comparison_type': 'OFFICIAL_JPL_ONLY',
                'status': 'SWISS_9999_NOT_REQUESTED', 'count': len(reference['observations']),
                'pass_count': None, 'pass': None,
                'note': 'Swiss PLUTO is barycenter; Swiss body center must be target ID 9999 plus sat/sepm9999.se1.'}
    swe = require_engine()
    values = []
    for stamp, obs in zip(epochs, reference['observations']):
        jd = jd_from_utc(datetime.fromisoformat(stamp).astimezone(timezone.utc))
        if target == 'PlutoCenter':
            # Swiss Ephemeris v2.10 defines planetary body centers as distinct
            # target IDs, not as FLG_CENTER_BODY applied to swe.PLUTO. Pluto = 9999.
            # This requires sat/sepm9999.se1 plus a configured ephemeris path.
            try:
                pos, flags, diag = compat_calc_ut(swe, jd, SWISS_PLUTO_BODY_CENTER_ID,
                                         swe.FLG_SWIEPH | swe.FLG_SPEED)
            except Exception as exc:
                raise RuntimeError(
                    'Swiss Pluto body center 9999 unavailable: install licensed '
                    'sat/sepm9999.se1 under --swiss-ephe-path; no fallback to Pluto barycenter'
                ) from exc
            if not (flags & swe.FLG_SWIEPH):
                raise RuntimeError('Swiss body-center calculation did not confirm Swiss ephemeris engine')
            engine = 'swisseph_sat_9999'
            # The modern binding can report nonfatal diagnostics even when the
            # requested Swiss file engine is confirmed by return flags.
            # Record these notes; do not confuse warning text with a target swap.
        else:
            pos, engine = calc_planet(jd, getattr(swe, TARGETS[target]['swiss']), swiss_engine, True)
        difference = 3600 * angular_distance(pos[0] % 360, obs['longitude_deg'])
        values.append({'utc_epoch': stamp, 'reference_longitude_deg': obs['longitude_deg'],
                       'swiss_longitude_deg': round(pos[0] % 360, 9),
                       'difference_arcsec': round(difference, 6), 'engine': engine,
                       'binding_message': diag if target == 'PlutoCenter' else '',
                       'pass': difference <= tolerance_arcsec})
    return {'target': target, 'target_id': TARGETS[target]['horizons_id'],
            'requested_swiss_engine': swiss_engine,
            'comparison_type': 'MATCHED_HORIZONS_TARGET_VS_SWISS',
            'status': 'PASS' if all(x['pass'] for x in values) else 'FAIL',
            'count': len(values), 'pass_count': sum(x['pass'] for x in values),
            'pass': all(x['pass'] for x in values), 'data': values}


def spherical_offset_arcsec(a: dict, b: dict) -> float:
    """Great-circle separation on unit celestial sphere, robust at small angles."""
    lat_a, lat_b = math.radians(a['latitude_deg']), math.radians(b['latitude_deg'])
    dlat = lat_a - lat_b
    dlon = math.radians(((a['longitude_deg'] - b['longitude_deg'] + 180) % 360) - 180)
    h = math.sin(dlat / 2)**2 + math.cos(lat_a) * math.cos(lat_b) * math.sin(dlon / 2)**2
    return math.degrees(2 * math.asin(math.sqrt(min(1, max(0, h))))) * 3600


def compare_jpl_pluto_pair(references: dict, separation_limit_arcsec: float = 1.0) -> dict:
    """Only actual two-target JPL values can be paired. Swiss data are not used."""
    if not 0 < separation_limit_arcsec <= 3600:
        raise ValueError('Invalid separation limit')
    if 'PlutoBarycenter' not in references or 'PlutoCenter' not in references:
        return {'status': 'NOT_CHECKED_PAIR_INCOMPLETE', 'pass': None}
    bary = references['PlutoBarycenter']['observations']
    center = references['PlutoCenter']['observations']
    if len(bary) != len(center):
        raise ValueError('Pluto center and barycenter have different row counts')
    data = []
    for a, b in zip(bary, center):
        if abs(a['julian_day_ut'] - b['julian_day_ut']) > 1 / 864000:
            raise ValueError('Pluto center and barycenter time mismatch')
        difference = spherical_offset_arcsec(a, b)
        data.append({'julian_day_ut': a['julian_day_ut'],
                     'barycenter_deg': {'lon': a['longitude_deg'], 'lat': a['latitude_deg']},
                     'body_center_deg': {'lon': b['longitude_deg'], 'lat': b['latitude_deg']},
                     'angular_separation_arcsec': round(difference, 8),
                     'pass': difference <= separation_limit_arcsec})
    return {'status': 'PASS_OFFICIAL_PAIR_NUMERICAL' if all(d['pass'] for d in data)
            else 'FAIL_OFFICIAL_PAIR_NUMERICAL',
            'target_ids': [9, 999], 'reference_center': 399,
            'separation_limit_arcsec': separation_limit_arcsec,
            'max_separation_arcsec': max(d['angular_separation_arcsec'] for d in data),
            'pass': all(d['pass'] for d in data), 'data': data,
            'note': 'Threshold validates this finite set only; not a universal physical bound; not a Swiss body-center check.'}


def fetch_one(target: str, epochs: tuple[str, ...], timeout_seconds: float,
              tolerance_arcsec: float, compare_swiss_center: bool = False,
              contact: str = '', swiss_engine: str = 'moseph') -> tuple[dict, dict]:
    url, jds = build_official_url(target, epochs)
    contact = validate_contact(contact)
    request = Request(url, headers={
        'User-Agent': f'symbolic-reflection-support/{VERSION} (contact: {contact})',
        'Accept': 'application/json',
    })
    # One request at a time; retry only transient HTTP failures, never a DNS error.
    for attempt in range(3):
        try:
            with urlopen(request, timeout=timeout_seconds) as stream:
                actual = urlsplit(stream.geturl())
                if actual.scheme != 'https' or actual.netloc != 'ssd.jpl.nasa.gov' \
                        or actual.path != '/api/horizons.api':
                    raise ValueError('Redirect changed NASA/JPL official origin')
                if stream.status != 200:
                    raise OSError(f'Horizons returned HTTP {stream.status}')
                buf = stream.read(3_000_001)
                if len(buf) > 3_000_000:
                    raise ValueError('Horizons response unexpectedly long')
            break
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503) or attempt == 2:
                raise
            time.sleep(2 ** attempt)
    raw = buf.decode('utf-8')
    ref = parse_horizons_payload(raw, target, jds)
    comparison = compare_external(target, epochs, ref, tolerance_arcsec, compare_swiss_center,
                                  swiss_engine=swiss_engine)
    entry = {'target': target, 'target_id': TARGETS[target]['horizons_id'],
             'requested_url': url, 'source': 'OFFICIAL_HTTPS_TLS_ORIGIN_OBSERVED',
             'raw_api_sha256': hashlib.sha256(buf).hexdigest(), 'raw_api_response': raw,
             'comparison': comparison,
             'note': 'Not a cryptographically signed NASA attestation; TLS verified in source session.'}
    return entry, ref


def audit_summary(references: dict, comparisons: dict, tolerance: float,
                  strict_center: bool) -> dict:
    pair = compare_jpl_pluto_pair(references)
    matched = [v for v in comparisons.values() if v.get('pass') is not None]
    all_ok = bool(matched) and all(v['pass'] for v in matched)
    if pair['pass'] is False:
        all_ok = False
    if strict_center and pair['pass'] is None:
        all_ok = False
    return {'status': 'PASS_MATCHED_TARGETS_AND_OFFICIAL_PAIR' if all_ok and pair['pass'] is True
            else 'PASS_MATCHED_TARGETS_ONLY' if all_ok else 'FAIL_OR_INCOMPLETE',
            'matched_targets': [x['target'] for x in matched],
            'matched_target_comparisons': sum(x['count'] for x in matched),
            'matched_target_passed': sum(x['pass_count'] for x in matched),
            'pluto_official_pair': pair, 'tolerance_arcsec': tolerance,
            'any_mismatch': not all_ok,
            'notes': [
                'Default Swiss Pluto means Pluto-system barycenter: JPL 9, not JPL 999.',
                'Pluto center 999 is fetched separately, not compared to default Swiss Pluto.',
                'This calculation does not authenticate an archive independent of its original HTTPS fetch.',
                'Numerical ephemeris accuracy is unrelated to predictive validity of astrology.',
            ]}


def run_live(output_dir: Path, epochs: tuple[str, ...] = PUBLIC_EPOCHS,
             timeout_seconds: float = 30.0, tolerance_arcsec: float = 30.0,
             targets: tuple[str, ...] = DEFAULT_TARGETS,
             compare_swiss_center: bool = False, contact: str = '',
             swiss_engine: str = 'moseph') -> dict:
    names = normalize_targets(targets)
    contact = validate_contact(contact)
    if not 1 <= timeout_seconds <= 120:
        raise ValueError('Timeout must be 1..120 seconds')
    output_dir.mkdir(parents=True, exist_ok=True)
    references, comparisons, files = {}, {}, []
    for target in names:
        try:
            entry, ref = fetch_one(target, epochs, timeout_seconds, tolerance_arcsec,
                                   compare_swiss_center, contact, swiss_engine)
        except Exception as exc:
            url, _ = build_official_url(target, epochs)
            failure = {'schema_version': VERSION, 'status': 'OFFICIAL_FETCH_INCOMPLETE',
                       'target_failed': target, 'requested_url': url,
                       'received_targets': list(references),
                       'error_type': type(exc).__name__, 'error': str(exc),
                       'note': 'No fabricated ephemerides; inspect network/DNS and retry in an allowed environment.'}
            (output_dir / 'fetch_failure.json').write_text(
                json.dumps(failure, ensure_ascii=False, indent=2), encoding='utf-8')
            (output_dir / 'manifest.json').write_text(
                json.dumps({'schema_version': VERSION, 'source': 'OFFICIAL_ATTEMPT_INCOMPLETE',
                            'files': files, **failure}, ensure_ascii=False, indent=2), encoding='utf-8')
            raise
        name = f"horizons_{target.lower()}_public.json"
        # Two deliberately different hash scopes. The manifest's raw_sha256 is
        # the NASA HTTP response; archived_json_sha256 is the complete saved JSON.
        saved = json.dumps(entry, indent=2, ensure_ascii=False).encode('utf-8')
        (output_dir / name).write_bytes(saved)
        references[target], comparisons[target] = ref, entry['comparison']
        files.append({'target': target, 'filename': name,
                      'raw_sha256': entry['raw_api_sha256'],
                      'archived_json_sha256': hashlib.sha256(saved).hexdigest()})
        time.sleep(1.0)
    summary = audit_summary(references, comparisons, tolerance_arcsec, 'PlutoCenter' in names)
    manifest = {'schema_version': VERSION, 'source': 'LIVE_OFFICIAL_JPL_HTTPS_TLS',
                'official_host': HORIZONS_URL, 'swiss_engine': swiss_engine, 'epochs_utc': list(epochs), 'targets': list(names),
                'files': files, **summary}
    (output_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    # A previous failed attempt can leave this file even after the new PASS.
    # A successful live audit removes only this stale failure marker.
    (output_dir / 'fetch_failure.json').unlink(missing_ok=True)
    return manifest


def verify_archive(archive_dir: Path, epochs: tuple[str, ...] = PUBLIC_EPOCHS,
                   tolerance_arcsec: float = 30.0,
                   targets: tuple[str, ...] = DEFAULT_TARGETS,
                   compare_swiss_center: bool = False,
                   swiss_engine: str = 'moseph') -> dict:
    names = normalize_targets(targets)
    references, comparisons = {}, {}
    manifest_path = archive_dir / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else None
    expected_files = {f['target']: f for f in manifest.get('files', [])} if manifest else {}
    archived_file_hash_count = 0
    for target in names:
        filename = f'horizons_{target.lower()}_public.json'
        file_bytes = (archive_dir / filename).read_bytes()
        item = json.loads(file_bytes.decode('utf-8'))
        if manifest:
            record = expected_files.get(target)
            if not record or record.get('filename') != filename:
                raise ValueError(f'{target} is missing/mismatched in manifest')
            if record.get('archived_json_sha256'):
                if hashlib.sha256(file_bytes).hexdigest() != record['archived_json_sha256']:
                    raise ValueError(f'{target} archived JSON file SHA-256 mismatch')
                archived_file_hash_count += 1
        buf = item['raw_api_response'].encode('utf-8')
        if hashlib.sha256(buf).hexdigest() != item['raw_api_sha256']:
            raise ValueError(f'{target} raw HTTP response SHA-256 mismatch')
        if manifest and record.get('raw_sha256') != item['raw_api_sha256']:
            raise ValueError(f'{target} manifest raw HTTP response SHA-256 mismatch')
        url, jds = build_official_url(target, epochs)
        if item.get('requested_url') != url:
            raise ValueError(f'{target} archive request URL differs from expected canonical URL')
        ref = parse_horizons_payload(item['raw_api_response'], target, jds)
        references[target] = ref
        comparisons[target] = compare_external(target, epochs, ref, tolerance_arcsec,
                                               compare_swiss_center, swiss_engine=swiss_engine)
    summary = audit_summary(references, comparisons, tolerance_arcsec, 'PlutoCenter' in names)
    result = {'schema_version': VERSION, 'source': 'LOCAL_ARCHIVE_NOT_REAUTHENTICATED',
              'targets': list(names), 'epochs_utc': list(epochs), 'swiss_engine': swiss_engine, **summary}
    result['status'] = ('PASS_ARCHIVED_NUMERIC_ONLY' if summary['status'].startswith('PASS')
                        else 'FAIL_ARCHIVED_NUMERIC_OR_INCOMPLETE')
    result['archive_integrity'] = {
        'raw_api_sha256_checked': bool(manifest),
        'archived_json_sha256_checked': archived_file_hash_count,
        'archive_file_count': len(names),
        'legacy_manifest_without_file_sha256': archived_file_hash_count < len(names),
        'note': 'Archive integrity does not independently authenticate the original NASA TLS session.',
    }
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='NASA/JPL Horizons: Moon 301, Pluto barycenter 9, Pluto center 999; audit, not prediction')
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument('--fetch', action='store_true', help='Make HTTPS calls to official NASA/JPL host')
    src.add_argument('--from-archive', type=Path, help='Recompute audit from saved raw API JSON (not reauthenticated)')
    src.add_argument('--check-center-ephe', action='store_true', help='Local offline Swiss 9999 data check only; no NASA query')
    p.add_argument('--targets', nargs='+', choices=tuple(TARGETS), default=list(DEFAULT_TARGETS))
    p.add_argument('--output-dir', type=Path, default=Path('horizons-audit-output'))
    p.add_argument('--swiss-ephe-path', type=Path, default=None,
                   help='Optional path containing Swiss satellite/Pluto-center ephemeris files')
    p.add_argument('--compare-swiss-center', action='store_true',
                   help='Also compare Horizons 999 to Swiss body ID 9999; requires licensed sat/sepm9999.se1')
    p.add_argument('--contact', default=None, help='Your email or HTTPS project URL (JPL API fair use; required for --fetch)')
    p.add_argument('--tolerance-arcsec', type=float, default=30.0)
    p.add_argument('--timeout', type=float, default=30.0)
    p.add_argument('--swiss-engine', choices=('moseph','swieph'), default='moseph',
                   help='Swiss mode for Moon and Pluto barycenter (strict actual flag). Swiss 9999 always requires SWIEPH.')
    p.add_argument('--strict', action='store_true')
    a = p.parse_args(argv)
    try:
        if a.check_center_ephe:
            if not a.swiss_ephe_path:
                raise ValueError('--check-center-ephe requires --swiss-ephe-path DIR with sat/sepm9999.se1')
            result = check_swiss_body_center(a.swiss_ephe_path)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if a.compare_swiss_center:
            if not a.swiss_ephe_path:
                raise ValueError('--compare-swiss-center requires --swiss-ephe-path DIR (containing sat/sepm9999.se1)')
            require_engine().set_ephe_path(str(verify_center_ephemeris_directory(a.swiss_ephe_path)))
        elif a.swiss_ephe_path:
            require_engine().set_ephe_path(str(a.swiss_ephe_path))
        if a.compare_swiss_center and 'PlutoCenter' not in a.targets:
            raise ValueError('--compare-swiss-center requires --targets PlutoCenter')
        if a.fetch:
            result = run_live(a.output_dir, timeout_seconds=a.timeout,
                              tolerance_arcsec=a.tolerance_arcsec,
                              targets=tuple(a.targets), compare_swiss_center=a.compare_swiss_center, swiss_engine=a.swiss_engine,
                              contact=(a.contact or os.environ.get('SRS_HORIZONS_CONTACT', '')))
        else:
            result = verify_archive(a.from_archive, tolerance_arcsec=a.tolerance_arcsec,
                                    targets=tuple(a.targets), compare_swiss_center=a.compare_swiss_center,
                                    swiss_engine=a.swiss_engine)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if a.strict and (result['any_mismatch'] or result['status'].startswith('FAIL')):
            return 1
        return 0
    except (OSError, TimeoutError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        print('fetch_horizons: NOT_VERIFIED: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
