"""Independent-model QA and installation checks.

The model is deliberately lower precision than Swiss. Do not label this
suite as NASA/JPL Horizons/DE440 numerical cross-verification.
"""
import importlib.util
import sys
from pathlib import Path
import unittest
from datetime import datetime,timezone

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from ephemeris_reference import (BODIES,EXCLUDED,tropical_longitude_approx,jd_from_utc,
                                   angular_distance,independent_asc_mc,moon_approximate_longitude)
from verify_ephemeris import (PUBLIC_CASES,TOLERANCES_DEG,compare_case)
from compare_horizons_fixture import compare
from install_diagnostics import diagnose

class IndependentMathTests(unittest.TestCase):
    def test_9_supported_not_pluto(self):
        self.assertEqual(len(BODIES),9)
        self.assertEqual(EXCLUDED,('Pluto',))
        jd=2451545.0
        for body in BODIES:
            self.assertTrue(0<=tropical_longitude_approx(body,jd)<360)
        with self.assertRaises(ValueError):tropical_longitude_approx('Pluto',jd)

    def test_period_limit(self):
        with self.assertRaises(ValueError):tropical_longitude_approx('Mercury',2_300_000.0)

    def test_jd_independent_of_swiss(self):
        self.assertAlmostEqual(jd_from_utc(datetime(2000,1,1,12,tzinfo=timezone.utc)),2451545.0,places=6)
        with self.assertRaises(ValueError):jd_from_utc(datetime(2000,1,1,12))

    def test_longitude_wrapping(self):
        self.assertAlmostEqual(angular_distance(359.95,.05),.1,places=8)

    def test_asc_mc_geometry_standalone(self):
        asc,mc=independent_asc_mc(2451545.0,51.4779,0.0)
        self.assertTrue(0<=asc<360 and 0<=mc<360)

    def test_invalid_horizons_fixtures_rejected(self):
        with self.assertRaises(ValueError):compare({'metadata':{'center':'500@399','quantity':'31','coordinate_type':'observer_ecliptic_of_date_apparent','time_scale':'UTC'},'observations':[]})
        with self.assertRaises(ValueError):compare({'metadata':{'center':'500@399','quantity':'18','coordinate_type':'observer_ecliptic_of_date_apparent','time_scale':'UTC'},'observations':[{'body':'Sun','utc':'2000-01-01T12:00:00+00:00','longitude_deg':280.0}]})

    def test_external_ref_schema_does_not_claim_authenticated(self):
        import inspect
        self.assertIn('USER_SUPPLIED_NOT_AUTHENTICATED',inspect.getsource(compare))

@unittest.skipUnless(importlib.util.find_spec('swisseph'),'optional astronomy extra not installed')
class IndependentComparisonTests(unittest.TestCase):
    def test_all_public_cases_pass_loose_tolerances(self):
        for utc,lat,lon in PUBLIC_CASES:
            with self.subTest(utc=utc):
                c=compare_case(utc,lat,lon)
                self.assertEqual(c['status'],'PASS_MODEL_LEVEL')
                self.assertEqual(c['passed'],11)
                self.assertEqual(c['count'],11)
                self.assertIn('Pluto',c['not_covered'])

    def test_diagnostic_script_privacy_and_separate_check(self):
        # Avoid nested shell execution inside full-suite discovery: install
        # diagnostics is exercised separately in CI as a real process.
        import inspect
        source=inspect.getsource(diagnose)
        self.assertIn('No birth data',source)
        self.assertNotIn('gethostname(',source)
        self.assertNotIn('gethostbyname(',source)

    def test_reference_comparator_not_fake_high_precision(self):
        # An intentionally FAR OFF, explicitly synthetic fixture must FAIL.
        fixture={'metadata':{'center':'500@399','quantity':'31',
                   'coordinate_type':'observer_ecliptic_of_date_apparent','time_scale':'UTC',
                   'source_description':'synthetic negative test'},
                 'observations':[{'body':'Sun','utc':'2000-01-01T12:00:00+00:00',
                                  'longitude_deg':90.0}]}
        report=compare(fixture)
        self.assertEqual(report['status'],'FAIL_USER_SUPPLIED_FIXTURE')
        self.assertEqual(report['provenance'],'USER_SUPPLIED_NOT_AUTHENTICATED')

if __name__=='__main__':unittest.main()
