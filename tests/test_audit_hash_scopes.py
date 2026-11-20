"""Offline integrity regression using MOCK Horizons responses; never JPL provenance."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from fetch_horizons import run_live, verify_archive, build_official_url, PUBLIC_EPOCHS
from check_horizons_hashes import validate_folder


class HashScopeTests(unittest.TestCase):
    def build_mock(self):
        _, jds = build_official_url('Moon')
        observations = [{'julian_day_ut': jd, 'longitude_deg': 100., 'latitude_deg': 1.} for jd in jds]
        result_lines = '\n'.join(f'{jd:.9f}, , , 100.0000000, 1.0000000,' for jd in jds)
        raw_http = json.dumps({
            'signature': {'source': 'NASA/JPL Horizons API', 'version': 'MOCK-ONLY'},
            'result': ('Target body name: Moon (301)\nCenter body name: Earth (399)\n'
                       'Date__(UT)__JDUT, , , ObsEcLon, ObsEcLat\n$$SOE\n'
                       + result_lines + '\n$$EOE'),
        })
        raw_digest = hashlib.sha256(raw_http.encode('utf-8')).hexdigest()
        entry = {
            'target':'Moon','target_id':301, 'requested_url':build_official_url('Moon')[0],
            'source':'MOCK_ONLY_NOT_OFFICIAL', 'raw_api_sha256':raw_digest,
            'raw_api_response':raw_http,
            'comparison': {'target':'Moon', 'count':4, 'pass_count':4, 'pass':True},
        }
        return entry, {'observations': observations}

    def test_new_manifest_hashes_both_scopes_and_detects_modified_json(self):
        entry, reference = self.build_mock()
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            with patch('fetch_horizons.fetch_one', return_value=(entry, reference)), patch('fetch_horizons.time.sleep'):
                manifest = run_live(folder, targets=('Moon',), contact='testing@example.org')
            self.assertIn('archived_json_sha256', manifest['files'][0])
            self.assertNotEqual(manifest['files'][0]['raw_sha256'], manifest['files'][0]['archived_json_sha256'])
            self.assertEqual(validate_folder(folder)['status'], 'PASS_BOTH_HASH_SCOPES')
            # Changing whitespace of the wrapper leaves the raw JPL payload unchanged.
            fp = folder / 'horizons_moon_public.json'
            fp.write_bytes(fp.read_bytes() + b'\n')
            result = validate_folder(folder)
            self.assertEqual(result['status'], 'FAIL')
            self.assertTrue(result['files'][0]['raw_http_sha256_matches_manifest'])
            self.assertFalse(result['files'][0]['saved_json_sha256_matches_manifest'])
            with self.assertRaisesRegex(ValueError, 'archived JSON file SHA-256 mismatch'):
                verify_archive(folder, targets=('Moon',))

    def test_legacy_manifest_raw_sha_only_is_not_falsely_marked_tampered(self):
        entry, reference = self.build_mock()
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            with patch('fetch_horizons.fetch_one', return_value=(entry, reference)), patch('fetch_horizons.time.sleep'):
                run_live(folder, targets=('Moon',), contact='testing@example.org')
            p=folder/'manifest.json'; manifest=json.loads(p.read_text(encoding='utf-8'))
            for row in manifest['files']:
                row.pop('archived_json_sha256')
            p.write_text(json.dumps(manifest), encoding='utf-8')
            self.assertEqual(validate_folder(folder)['status'], 'PASS_RAW_ONLY_LEGACY')
            with patch('fetch_horizons.compare_external', return_value={'target':'Moon','count':4,'pass_count':4,'pass':True}):
                output=verify_archive(folder, targets=('Moon',))
            self.assertTrue(output['archive_integrity']['legacy_manifest_without_file_sha256'])
            self.assertEqual(output['archive_integrity']['archived_json_sha256_checked'],0)

    def test_embedded_http_body_tamper_is_rejected(self):
        entry, reference = self.build_mock()
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            with patch('fetch_horizons.fetch_one', return_value=(entry, reference)), patch('fetch_horizons.time.sleep'):
                run_live(folder, targets=('Moon',), contact='testing@example.org')
            fp=folder/'horizons_moon_public.json'
            payload=json.loads(fp.read_text(encoding='utf-8'))
            payload['raw_api_response']=payload['raw_api_response'].replace('100.0000000','101.0000000')
            fp.write_text(json.dumps(payload), encoding='utf-8')
            self.assertEqual(validate_folder(folder)['status'],'FAIL')
            self.assertFalse(validate_folder(folder)['files'][0]['raw_http_sha256_matches_manifest'])

    def test_old_failure_marker_removed_after_new_success(self):
        entry, reference = self.build_mock()
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);(folder/'fetch_failure.json').write_text('{"status":"stale"}')
            with patch('fetch_horizons.fetch_one', return_value=(entry, reference)), patch('fetch_horizons.time.sleep'):
                run_live(folder, targets=('Moon',), contact='testing@example.org')
            self.assertFalse((folder/'fetch_failure.json').exists())

    def test_unsafe_manifest_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            (folder/'manifest.json').write_text(json.dumps({'files':[{'filename':'../secret.json', 'target':'Moon'}]}))
            with self.assertRaisesRegex(ValueError,'Unsafe archived filename'):
                validate_folder(folder)

if __name__ == '__main__': unittest.main()
