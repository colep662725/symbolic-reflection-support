"""v1.3.2 independent Placidus geometry + strict Horizons fetch/parser tests.

NO synthetic Horizons value is treated as a verified JPL fixture.
"""
import importlib.util
import json
from datetime import datetime,timezone
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch,MagicMock
from urllib.parse import parse_qs,urlsplit

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from placidus_independent import (sidereal_obliquity_independent,placidus_cusps_from_angles,
                                  independent_placidus,circular_distance)
from fetch_horizons import (build_official_url,parse_horizons_payload,fetch_one,PUBLIC_EPOCHS)
from verify_placidus import PUBLIC_CASES as HOUSE_CASES, run as run_houses

class GeometryOnlyTests(unittest.TestCase):
    def test_nonpolar_asc_mc_opposition(self):
        m=independent_placidus(2451545.0,30.0,0.0)
        cusp=m['cusps_deg']
        self.assertEqual(len(cusp),12)
        for i in range(6):self.assertLess(circular_distance(cusp[i],(cusp[i+6]+180)%360),1e-9)

    def test_equator_semarc_trisection(self):
        c=placidus_cusps_from_angles(90,23.44,0)
        self.assertLess(circular_distance(c[10],117.91042265),0.001) # analytic equatorial-latitude expectation
        for i in range(12):self.assertLess((c[(i+1)%12]-c[i])%360,60)

    def test_no_silent_polar_substitution(self):
        with self.assertRaisesRegex(ValueError,'latitude'):placidus_cusps_from_angles(90,23.44,70)

    def test_sidereal_obliquity_independent(self):
        th,eps=sidereal_obliquity_independent(2451545.0,0)
        self.assertTrue(0<=th<360)
        self.assertTrue(23<eps<24)

class StrictHorizonsContractTests(unittest.TestCase):
    def test_public_epoch_urls_distinguish_targets(self):
        for body,code in [('Moon','301'),('PlutoBarycenter','9'),('PlutoCenter','999')]:
            url,jds=build_official_url(body)
            self.assertEqual(len(jds),4)
            parsed=parse_qs(urlsplit(url).query)
            self.assertEqual(parsed['COMMAND'],[f"'{code}'"])
            self.assertEqual(parsed['CENTER'],["'500@399'"])
            self.assertEqual(parsed['QUANTITIES'],["'31'"])
            self.assertEqual(parsed['TIME_TYPE'],["'UT'"])
            self.assertEqual(parsed['TLIST_TYPE'],["'JD'"])
            self.assertEqual(len(re.findall(r"'\d+\.\d+'",parsed['TLIST'][0])),4)
            self.assertNotIn('START_TIME',parsed)
            self.assertNotIn('STOP_TIME',parsed)

    def test_no_fabricated_jpl_when_missing_table(self):
        fixture={'signature':{'source':'NASA/JPL Horizons API','version':'1.3'},'result':'No ephemeris was generated'}
        with self.assertRaisesRegex(ValueError,r'\$\$SOE'):parse_horizons_payload(json.dumps(fixture),'Moon',[2451545.0])

    def test_reject_source_spoof(self):
        fixture={'signature':{'source':'untrusted','version':'1.3'},'result':'$$SOE 123 $$EOE ObsEcLon ObsEcLat'}
        with self.assertRaisesRegex(ValueError,'NASA/JPL'):parse_horizons_payload(json.dumps(fixture),'Moon',[2451545.0])

    def test_reject_wrong_target_and_timestamps(self):
        head='Target body name: Pluto (999)\nCenter body name: Earth (399)\nObsEcLon ObsEcLat\n$$SOE\n2451545.0, , , 123.45, -1.5,\n$$EOE'
        fixture={'signature':{'source':'NASA/JPL Horizons API','version':'1.3'},'result':head}
        with self.assertRaisesRegex(ValueError,'target body header'):parse_horizons_payload(json.dumps(fixture),'Moon',[2451545.0])
        with self.assertRaisesRegex(ValueError,'timestamp mismatch'):parse_horizons_payload(json.dumps(fixture),'PlutoCenter',[2451546.0])

    def test_reject_non_geocentric_center(self):
        fake={'signature':{'source':'NASA/JPL Horizons API','version':'MOCK'},
              'result':'Target body name: Moon (301)\nCenter body name: Mars (499)\n'
                       'ObsEcLon ObsEcLat\n$$SOE\n2451545.0, , , 123.45, -1.5,\n$$EOE'}
        with self.assertRaisesRegex(ValueError,'geocentric Earth'):
            parse_horizons_payload(json.dumps(fake),'Moon',[2451545.0])

    def test_synthetic_parser_does_not_authenticate_reference(self):
        # Synthetic payload to exercise parser only. This is NOT a JPL observation.
        fixture={'signature':{'source':'NASA/JPL Horizons API','version':'MOCK'},
                 'result':'Target body name: Moon (301)\nCenter body name: Earth (399)\n'
                          'Date__(UT)__JDUT  ObsEcLon ObsEcLat\n$$SOE\n2451545.0, , , 123.45, -1.5,\n$$EOE'}
        rows=parse_horizons_payload(json.dumps(fixture),'Moon',[2451545.0])
        self.assertEqual(rows['observations'][0]['longitude_deg'],123.45)
        self.assertEqual(rows['signature']['version'],'MOCK')

    def test_http_downloader_fails_closed_without_connection(self):
        with patch('fetch_horizons.urlopen',side_effect=OSError('network unavailable')):
            with self.assertRaisesRegex(OSError,'network unavailable'):
                fetch_one('Moon',PUBLIC_EPOCHS,2.0,30.0,contact='test@example.org')

@unittest.skipUnless(importlib.util.find_spec('swisseph'),'optional astronomy extra not installed')
class FullHouseTests(unittest.TestCase):
    def test_12_public_cases_all_12_cusps(self):
        r=run_houses(HOUSE_CASES)
        self.assertEqual(r['checks'],144)
        self.assertEqual(r['status'],'PASS_INDEPENDENT_GEOMETRY_MODEL')
        self.assertLess(r['max_full_pipeline_arcsec'],2.0)
        self.assertLess(r['max_geometry_only_arcsec'],.01)

if __name__=='__main__':unittest.main()
