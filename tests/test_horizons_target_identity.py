"""Identity contract checks. Synthetic tables are NEVER astronomy evidence."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from fetch_horizons import (build_official_url, parse_horizons_payload,
                            compare_external, compare_jpl_pluto_pair,
                            spherical_offset_arcsec, normalize_targets,
                            SWISS_PLUTO_BODY_CENTER_ID, validate_contact,
                            verify_center_ephemeris_directory, run_live,
                            check_swiss_body_center)


def example_record(jd, lon, lat=0):
    return {'julian_day_ut': jd, 'longitude_deg': lon, 'latitude_deg': lat}


class TargetIdentityTests(unittest.TestCase):
    def test_default_swiss_pluto_is_jpl_9(self):
        for target, number in [('Moon', 301), ('PlutoBarycenter', 9), ('PlutoCenter', 999)]:
            url, jds = build_official_url(target)
            self.assertEqual(parse_qs(urlsplit(url).query)['COMMAND'], [f"'{number}'"])
            self.assertEqual(parse_qs(urlsplit(url).query)['CENTER'], ["'500@399'"])
            self.assertEqual(len(jds), 4)

    def test_old_ambiguous_pluto_target_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unknown Horizons target'):
            build_official_url('Pluto')

    def test_duplicate_target_rejected(self):
        with self.assertRaises(ValueError):
            normalize_targets(['Moon', 'Moon'])

    def test_mismatched_target_header_rejected(self):
        url, jds = build_official_url('PlutoBarycenter', ('2000-01-01T12:00:00+00:00',))
        fake = {
          'signature': {'source': 'NASA/JPL Horizons API', 'version': 'MOCK'},
          'result': 'Target body name: Pluto (999)\nCenter body name: Earth (399)\n'
                    'ObsEcLon ObsEcLat\n$$SOE\n2451545.0, , , 250.0, 10.0,\n$$EOE'}
        with self.assertRaisesRegex(ValueError, 'target body header'):
            parse_horizons_payload(json.dumps(fake), 'PlutoBarycenter', jds)

    def test_body_center_uncompared_by_default(self):
        ref = {'observations': [example_record(2451545.0, 100)]}
        r = compare_external('PlutoCenter', ('2000-01-01T12:00:00+00:00',), ref, 30)
        self.assertIsNone(r['pass'])
        self.assertEqual(r['status'], 'SWISS_9999_NOT_REQUESTED')

    def test_no_silent_fallback_when_satellite_ephemeris_missing(self):
        class BrokenSwiss:
            PLUTO, FLG_SWIEPH, FLG_SPEED, FLG_CENTER_BODY = 9, 2, 256, 1048576
            def calc_ut(self, jd, body, flags):
                assert body == 9999, 'Expected Pluto body center object 9999'
                assert not (flags & self.FLG_CENTER_BODY), 'CENTER_BODY flag not valid approach'
                raise RuntimeError('Swiss Pluto center ephemeris missing')
        ref = {'observations': [example_record(2451545.0, 100)]}
        with patch('fetch_horizons.require_engine', return_value=BrokenSwiss()):
            with self.assertRaisesRegex(RuntimeError, '9999 unavailable'):
                compare_external('PlutoCenter', ('2000-01-01T12:00:00+00:00',), ref, 30, True)

    def test_separate_jpl_body_center_barycenter_contract(self):
        a = example_record(2451545.0, 350, 2.5)
        b = example_record(2451545.0, 350.000015, 2.5)
        r = compare_jpl_pluto_pair({'PlutoBarycenter': {'observations': [a]},
                                    'PlutoCenter': {'observations': [b]}})
        self.assertTrue(r['pass'])
        self.assertEqual(r['target_ids'], [9, 999])
        self.assertGreater(r['max_separation_arcsec'], 0)
        self.assertLess(r['max_separation_arcsec'], 0.1)

    def test_pluto_pair_needs_both_targets(self):
        r = compare_jpl_pluto_pair({'PlutoBarycenter': {'observations': [example_record(1, 2)]}})
        self.assertIsNone(r['pass'])

    def test_pluto_pair_rejects_time_mismatch(self):
        with self.assertRaisesRegex(ValueError, 'time mismatch'):
            compare_jpl_pluto_pair({'PlutoBarycenter': {'observations': [example_record(2451545.0, 2)]},
                                    'PlutoCenter': {'observations': [example_record(2451545.01, 2)]}})

    def test_great_circle_wrap_and_latitude(self):
        a = example_record(1, 359.9999, -2)
        b = example_record(1, 0.0001, -2)
        self.assertAlmostEqual(spherical_offset_arcsec(a, b), 0.72 * __import__('math').cos(__import__('math').radians(2)), places=3)

if __name__ == '__main__': unittest.main()
