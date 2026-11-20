"""v1.3 ephemeris, calendar algorithms, edge cases, model/independent reference checks.

No personal birth data stored in public fixtures. Independent published comparison:
Hong Kong Observatory 2024 official calendar (solar-term calendar dates),
HKO 60-cycle/ month/hour tables; public 2000-01-01 and 2024-02-10 almanac days.
Swiss Moshier regression is NOT independent ephemeris validation.
"""
from __future__ import annotations
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import subprocess
import sys
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE/'scripts'))
import calendar_core as core
import bazi
import natal
import solar_terms

HAS_SWE=core.swe is not None


def params(**kwargs):
    from argparse import Namespace
    opts=dict(datetime="2000-01-01T12:00:00",tz="Asia/Shanghai",lat=39.9042,lon=116.4074,fold=None,
              clock="civil",day_boundary="midnight",compare_boundaries=False,
              uncertainty_minutes=0,ephemeris="moseph",strict_ephemeris=False,
              direction="auto",traditional_sex=None,cycles=8,
              houses="placidus",cross_check=False)
    opts.update(kwargs)
    return Namespace(**opts)


class DayAndTimezoneTests(unittest.TestCase):
    def test_day_cycle_anchor_and_independent_2024_reference(self):
        self.assertEqual(core.sexagenary(bazi.daily_index(date(2000,1,1))), '戊午')
        self.assertEqual(core.sexagenary(bazi.daily_index(date(2024,2,10))), '甲辰')
        self.assertEqual(core.sexagenary(bazi.daily_index(date(2024,2,11))), '乙巳')

    def test_continuous_60_day_cycle(self):
        start=date(2020,1,1)
        for i in range(365):
            a=bazi.daily_index(start+timedelta(days=i))
            nxt=bazi.daily_index(start+timedelta(days=i+1))
            self.assertEqual(nxt,(a+1)%60)

    def test_midnight_convention_resolves_ambiguity_explicitly(self):
        local,utc=core.parse_birth('2024-11-03T01:30:00','America/New_York',fold=0)
        local1,utc1=core.parse_birth('2024-11-03T01:30:00','America/New_York',fold=1)
        self.assertEqual(abs((utc1-utc).total_seconds()),3600)
        with self.assertRaisesRegex(ValueError,'Ambiguous'):
            core.parse_birth('2024-11-03T01:30:00','America/New_York')
        with self.assertRaisesRegex(ValueError,'does not exist'):
            core.parse_birth('2024-03-10T02:30:00','America/New_York')

    def test_timezone_errors_and_birth_range(self):
        for d,tz in [('1999-01-01T12:00+08:00','Asia/Shanghai'),('1800-01-01T00:00','Asia/Shanghai')]:
            with self.assertRaises(ValueError): core.parse_birth(d,tz)
        with self.assertRaises(ValueError): core.parse_birth('2024-01-01T10:00','Nowhere/Atlantis')

    @unittest.skipUnless(HAS_SWE,'optional astronomy dependency unavailable')
    def test_clock_modes_and_apparent_offset(self):
        l,u=core.parse_birth('2024-06-01T12:00:00','Asia/Shanghai')
        civil,_=bazi.clock_wall_time(l,u,116.4,'civil')
        mean,info=bazi.clock_wall_time(l,u,116.4,'mean-solar')
        apparent,info2=bazi.clock_wall_time(l,u,116.4,'apparent-solar')
        self.assertEqual(civil.hour,12)
        self.assertAlmostEqual((mean-civil).total_seconds()/60,-14.4,places=3)
        self.assertNotAlmostEqual(info2['equation_of_time_minutes'],0,places=2)
        self.assertLess(abs((apparent-civil).total_seconds()/60),40)


@unittest.skipUnless(HAS_SWE,'optional astronomy dependency unavailable')
class SolarTermTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events=solar_terms.calculate(2024,'Asia/Shanghai','moseph',True,True)

    def test_24_terms_and_longitudes_and_numerical_roots(self):
        self.assertEqual(len(self.events['terms']),24)
        for e in self.events['terms']:
            self.assertLess(e['numerical_root_check']['residual_arcsec'],0.05)
            self.assertLess(e['bisection_difference_seconds'],0.5)
        self.assertEqual([x['name'] for x in self.events['terms']], [name for name,_ in solar_terms.TERMS])

    def test_22_independent_calendar_dates_from_hko_2024(self):
        # Source: https://www.hko.gov.hk/tc/gts/time/calendar/pdf/files/2024.pdf
        expected={
            '立春':'2024-02-04','雨水':'2024-02-19','惊蛰':'2024-03-05','春分':'2024-03-20',
            '清明':'2024-04-04','谷雨':'2024-04-19','立夏':'2024-05-05','小满':'2024-05-20',
            '芒种':'2024-06-05','夏至':'2024-06-21','小暑':'2024-07-06','大暑':'2024-07-22',
            '立秋':'2024-08-07','处暑':'2024-08-22','白露':'2024-09-07','秋分':'2024-09-22',
            '寒露':'2024-10-08','霜降':'2024-10-23','立冬':'2024-11-07','小雪':'2024-11-22',
            '大雪':'2024-12-06','冬至':'2024-12-21',
        }
        for x in self.events['terms']:
            if x['name'] in expected:
                self.assertEqual(x['local_calendar_date'],expected[x['name']],x['name'])

    def test_month_terms_only_12_and_jie_order(self):
        out=core.jie_boundaries(2024,strict=True)
        self.assertEqual(len(out),12)
        self.assertEqual([x['name'] for x in out],[x[0] for x in core.JIE])
        self.assertTrue(all(a['jd_ut']<b['jd_ut'] for a,b in zip(out,out[1:])))

    def test_lichen_boundary_instant_not_civil_day(self):
        lic=core.jie_boundaries(2024)[0]['jd_ut']
        from datetime import timezone
        for offset,name in [(-3,'癸卯'),(+3,'甲辰')]:
            t=core.datetime_from_jd(lic+offset/86400)
            loc=t.astimezone(__import__('zoneinfo').ZoneInfo('Asia/Shanghai'))
            ch,_,_=bazi.chart_at(loc,t,116.4,'midnight','civil','moseph',True)
            self.assertEqual(ch['year']['gan_zhi'],name)
        self.assertEqual(name,'甲辰')


@unittest.skipUnless(HAS_SWE,'optional astronomy dependency unavailable')
class BaziTests(unittest.TestCase):
    def test_independent_almanac_fixture_2000(self):
        x=bazi.compute(params())
        # 2000-01-01: 己卯年 丙子月 戊午日 (calendar published independently)
        self.assertEqual(x['pillars']['year']['gan_zhi'],'己卯')
        self.assertEqual(x['pillars']['month']['gan_zhi'],'丙子')
        self.assertEqual(x['pillars']['day']['gan_zhi'],'戊午')
        self.assertEqual(x['pillars']['hour']['gan_zhi'],'戊午')
        self.assertEqual(x['luck_cycles']['status'],'not computed; supply --direction or --traditional-sex; no sex/identity inferred')

    def test_independent_almanac_fixture_2024(self):
        x=bazi.compute(params(datetime='2024-02-10T12:00:00'))
        self.assertEqual(x['pillars']['eight_characters'],'甲辰丙寅甲辰庚午')

    def test_zi_variants_are_explicit_and_not_mixed(self):
        x=bazi.compute(params(datetime='2024-02-10T23:45:00',compare_boundaries=True))
        comp=x['boundary_comparison']
        self.assertEqual(comp['midnight']['day_master'],'甲')
        self.assertEqual(comp['zi-start']['day_master'],'乙')
        self.assertEqual(comp['split-zi']['day_master'],'甲')
        self.assertEqual(comp['zi-start']['eight_characters'][-2:],comp['split-zi']['eight_characters'][-2:])
        self.assertNotEqual(comp['midnight']['eight_characters'][-2:],comp['zi-start']['eight_characters'][-2:])

    def test_bazi_2_clock_systems_change_wall_time_not_event_instant(self):
        a=bazi.compute(params(datetime='2024-02-10T23:50:00',clock='civil'))
        b=bazi.compute(params(datetime='2024-02-10T23:50:00',clock='apparent-solar'))
        self.assertEqual(a['pillars']['year']['gan_zhi'],b['pillars']['year']['gan_zhi'])
        self.assertEqual(a['pillars']['month']['gan_zhi'],b['pillars']['month']['gan_zhi'])
        self.assertEqual(a['utc_datetime'],b['utc_datetime'])
        self.assertNotEqual(a['pillars']['basis']['clock']['method'],b['pillars']['basis']['clock']['method'])

    def test_luck_directions_and_auto_parameter(self):
        direct=bazi.compute(params(direction='forward',cycles=3))['luck_cycles']
        reverse=bazi.compute(params(direction='backward',cycles=3))['luck_cycles']
        self.assertEqual([x['gan_zhi'] for x in direct['cycles']],['丁丑','戊寅','己卯'])
        self.assertEqual([x['gan_zhi'] for x in reverse['cycles']],['乙亥','甲戌','癸酉'])
        self.assertNotEqual(direct['start_age_nominal_years'],reverse['start_age_nominal_years'])
        m=bazi.compute(params(traditional_sex='male',cycles=2))['luck_cycles']
        f=bazi.compute(params(traditional_sex='female',cycles=2))['luck_cycles']
        # 己阴年: male backward, female forward
        self.assertEqual(m['direction'],'backward')
        self.assertEqual(f['direction'],'forward')

    def test_luck_sensitivity_and_no_predictions(self):
        x=bazi.compute(params(direction='forward',uncertainty_minutes=30,compare_boundaries=True,cycles=2))
        self.assertFalse(x['predictions_supported'])
        self.assertEqual(len(x['birth_time_sensitivity']['endpoint_charts']),2)
        self.assertEqual(len(x['luck_cycles']['cycles']),2)

    def test_invalid_input_exits_nonzero(self):
        for args in [('--datetime','not-a-datetime'),('--datetime','2024-03-10T02:30:00','--tz','America/New_York'),
                     ('--datetime','2024-02-10T12:00:00','--direction','nonsense')]:
            p=subprocess.run([sys.executable,str(BASE/'scripts/bazi.py'),'--tz','Asia/Shanghai','--lat','39.9','--lon','116.4',*args],
                             capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)


@unittest.skipUnless(HAS_SWE,'optional astronomy dependency unavailable')
class NatalTests(unittest.TestCase):
    def test_natal_reference_2000_positions_regression_not_independent(self):
        x=natal.compute(params(tz='Europe/London',lat=51.4779,lon=0.0))
        chart=x['chart'];self.assertEqual(len(chart['planets']),10)
        self.assertAlmostEqual(chart['houses']['ascendant_deg'],24.2661892,places=4)
        self.assertAlmostEqual(chart['houses']['midheaven_deg'],279.6110878,places=4)
        self.assertAlmostEqual(chart['planets'][0]['longitude_deg'],280.36891968,places=4)
        self.assertEqual(chart['planets'][0]['zodiac']['sign_en'],'Capricorn')
        self.assertEqual(chart['planets'][0]['house'],10)
        self.assertFalse(x['predictions_supported'])
        self.assertEqual(x['astronomy']['effective_ephemeris'],'moseph')

    def test_whole_sign_ascendant_and_house_boundaries(self):
        p=params(tz='Europe/London',lat=51.4779,lon=0.0,houses='whole-sign')
        x=natal.compute(p)['chart']
        self.assertAlmostEqual(x['houses']['ascendant_deg'],24.2661892,places=4)
        self.assertEqual(x['houses']['cusps_deg'][0],0.0)
        self.assertEqual(x['houses']['cusps_deg'][1],30.0)
        self.assertEqual(natal.longitude_house(359,[30*i for i in range(12)]),12)
        self.assertEqual(natal.longitude_house(0,[30*i for i in range(12)]),1)

    def test_cross_check_does_not_claim_independent_when_fallback(self):
        x=natal.compute(params(tz='Europe/London',lat=51.4779,lon=0,cross_check=True))
        # CI ephemeris files are intentionally not bundled.
        if x['cross_check']['primary_effective_engines']==x['cross_check']['alternative_effective_engines']:
            self.assertEqual(x['cross_check']['status'],'NOT_INDEPENDENT_both_calls_used_same_effective_engine')
        self.assertGreaterEqual(x['cross_check']['max_angular_difference_arcsec'],0)

    def test_actual_swisseph_flag_reporting_fallback_is_not_hidden(self):
        x=natal.compute(params(tz='Europe/London',lat=51.4779,lon=0,ephemeris='swieph'))
        self.assertEqual(x['astronomy']['requested_ephemeris'],'swieph')
        self.assertIn(x['astronomy']['effective_ephemeris'],('moseph','swieph'))
        if x['astronomy']['effective_ephemeris']=='moseph':
            with self.assertRaisesRegex(RuntimeError,'Requested swieph'):
                natal.compute(params(tz='Europe/London',lat=51.4779,lon=0,ephemeris='swieph',strict_ephemeris=True))

    def test_house_time_sensitivity_and_missing_planet_houses(self):
        x=natal.compute(params(tz='Europe/London',lat=51.4779,lon=0,uncertainty_minutes=15))
        self.assertEqual(len(x['birth_time_sensitivity']['endpoints']),2)
        self.assertEqual(len(x['chart']['planets']),10)
        self.assertTrue(all(1<=p['house']<=12 for p in x['chart']['planets']))

    def test_extreme_location_rejects_instead_of_fabricating(self):
        with self.assertRaises(ValueError):natal.compute(params(lat=90))

    def test_cli_json_roundtrip(self):
        for cmd in ('bazi.py','natal.py','solar_terms.py'):
            if cmd=='solar_terms.py':args=['--year','2024','--tz','Asia/Shanghai']
            else:args=['--datetime','2000-01-01T12:00:00','--tz','Asia/Shanghai','--lat','39.9','--lon','116.4']
            proc=subprocess.run([sys.executable,str(BASE/'scripts'/cmd),*args],text=True,capture_output=True,check=True)
            d=json.loads(proc.stdout)
            self.assertEqual(d['schema_version'],'1.3.0')
            self.assertNotIn('personal_predictions',proc.stdout)

if __name__=='__main__':unittest.main()
