#!/usr/bin/env python3
"""Verify TWO SHA-256 scopes in a saved Horizons archive. No network or astrology.

- manifest.raw_sha256 / entry.raw_api_sha256: original HTTP payload bytes
- manifest.archived_json_sha256 (v1.3.5-rc2+): saved JSON wrapper bytes

Older archives contain only raw response hashes; their whole-file hash is not
independently committed by the old manifest. Results do not authenticate NASA
source provenance or the earlier TLS session.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def validate_folder(folder: Path) -> dict:
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    rows = []
    any_fail = False
    any_unrecorded = False
    for f in manifest.get('files', []):
        name = f['filename']
        path = folder / name
        # Never accept path traversal from a tampered manifest.
        if Path(name).name != name or not name.startswith('horizons_') or not name.endswith('_public.json'):
            raise ValueError(f'Unsafe archived filename: {name!r}')
        content = path.read_bytes()
        obj = json.loads(content.decode('utf-8'))
        response = obj['raw_api_response'].encode('utf-8')
        raw_actual = hashlib.sha256(response).hexdigest()
        file_actual = hashlib.sha256(content).hexdigest()
        raw_match = raw_actual == f.get('raw_sha256') == obj.get('raw_api_sha256')
        file_expected = f.get('archived_json_sha256')
        file_match = file_actual == file_expected if file_expected else None
        any_unrecorded |= file_match is None
        any_fail |= not raw_match or file_match is False
        rows.append({'target': f.get('target'), 'filename': name,
                     'raw_http_sha256_matches_manifest': raw_match,
                     'saved_json_sha256_matches_manifest': file_match,
                     'saved_json_sha256_current': file_actual,
                     'raw_http_sha256_current': raw_actual})
    if not rows:
        raise ValueError('No captured Horizons target files in manifest')
    status = ('FAIL' if any_fail else 'PASS_RAW_ONLY_LEGACY' if any_unrecorded
              else 'PASS_BOTH_HASH_SCOPES')
    return {'status': status, 'files': rows,
            'original_source_reauthenticated': False,
            'note': ('Hash checks establish internal file consistency only, not the ' 
                     'authenticity of a previous NASA HTTPS response.')}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate_folder(args.archive)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 1 if result['status'] == 'FAIL' else 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(2, 'INTEGRITY_NOT_VERIFIED: ' + str(exc) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
