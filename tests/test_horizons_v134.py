"""v1.3.4 protocol tests; all API-looking payloads below are MOCKS, not observations."""
import hashlib
import json
import tempfile
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from fetch_horizons import (SWISS_PLUTO_BODY_CENTER_ID, validate_contact,
                            verify_center_ephemeris_directory, build_official_url,
                            compare_external, run_live, parse_horizons_payload)


class ProtocolTests(TestCase):
    def test_correct_pluto_body_id_9999(self):
        self.assertEqual(SWISS_PLUTO_BODY_CENTER_ID, 9999)
        class MockSwiss:
            FLG_SWIEPH, FLG_SPEED, PLUTO, FLG_CENTER_BODY = 2, 256, 9, 1048576
            def calc_ut(self, jd, target, flags):
                self.requested = (jd, target, flags)
                return ([100.0, 0., 1., 0., 0., 0.], self.FLG_SWIEPH | self.FLG_SPEED)
        mock = MockSwiss()
        ref = {'observations': [{'julian_day_ut': 2451545., 'longitude_deg': 100., 'latitude_deg': 0.}]}
        with patch('fetch_horizons.require_engine', return_value=mock):
            result = compare_external('PlutoCenter', ('2000-01-01T12:00:00+00:00',), ref, 30., True)
        self.assertEqual(result['pass_count'], 1)
        self.assertEqual(mock.requested[1], 9999)
        self.assertFalse(mock.requested[2] & mock.FLG_CENTER_BODY)
        self.assertEqual(result['data'][0]['engine'], 'swisseph_sat_9999')

    def test_center_missing_engine_flag_is_failure(self):
        class Fake:
            FLG_SWIEPH, FLG_SPEED = 2, 256
            def calc_ut(self, jd, target, flags):
                return ([100., 0, 1, 0, 0, 0], self.FLG_SPEED)
        ref = {'observations': [{'longitude_deg':100.}]}
        with patch('fetch_horizons.require_engine', return_value=Fake()):
            with self.assertRaisesRegex(RuntimeError,'did not confirm Swiss'):
                compare_external('PlutoCenter', ('2000-01-01T12:00:00+00:00',), ref, 30., True)

    def test_center_file_missing_has_explanatory_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(FileNotFoundError, r'sat[\\/]sepm9999\.se1'):
                verify_center_ephemeris_directory(Path(tmp))

    def test_contact_fair_use(self):
        self.assertEqual(validate_contact('https://github.com/example/project'), 'https://github.com/example/project')
        self.assertEqual(validate_contact('contact@example.org'), 'contact@example.org')
        for invalid in ('', 'foo', 'http://example.org', 'bad\r\nHeader:x', 'https://a\nb'):
            with self.assertRaises(ValueError):
                validate_contact(invalid)

    def test_failure_manifest_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch('fetch_horizons.fetch_one', side_effect=OSError('mock DNS failure')):
                with self.assertRaisesRegex(OSError,'mock DNS'):
                    run_live(Path(tmp), contact='test@example.org', targets=('Moon',))
            failure = json.loads((Path(tmp)/'fetch_failure.json').read_text())
            manifest = json.loads((Path(tmp)/'manifest.json').read_text())
            self.assertEqual(failure['status'],'OFFICIAL_FETCH_INCOMPLETE')
            self.assertEqual(manifest['source'],'OFFICIAL_ATTEMPT_INCOMPLETE')
            self.assertEqual(failure['received_targets'],[])

    def test_real_api_shape_mock_target_integrity(self):
        url,jds=build_official_url('PlutoCenter', ('2000-01-01T12:00:00+00:00',))
        data={'signature':{'source':'NASA/JPL Horizons API','version':'TEST-MOCK'},
              'result':('Target body name: Pluto (999)\nCenter body name: Earth (399)\n'
                        'Date__(UT)__JDUT, , , ObsEcLon, ObsEcLat\n'
                        '$$SOE\n2451545.000000000, , , 251.1, 10.0,\n$$EOE')}
        parsed=parse_horizons_payload(json.dumps(data),'PlutoCenter',jds)
        self.assertEqual(parsed['observations'][0]['longitude_deg'],251.1)
        with self.assertRaisesRegex(ValueError,'target body header'):
            parse_horizons_payload(json.dumps(data),'PlutoBarycenter',jds)
