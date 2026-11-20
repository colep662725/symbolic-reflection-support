"""New and old Swiss Python binding ABI checks, including real calculations.

Modern ABI is simulated by wrapping the installed legacy C binding in a proxy;
this is NOT a claim that the tests ran the actual Windows pysweph wheel.
"""
from __future__ import annotations
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'scripts'))
import swiss_compat as compat
import calendar_core as core
import natal, bazi, verify_ephemeris, verify_placidus, fetch_horizons, solar_terms
import tempfile
from argparse import Namespace

class CompatShapeTests(unittest.TestCase):
    def test_legacy_and_modern_calc_tuple(self):
        vals=(120.,5.,1.,0.,0.,0.)
        self.assertEqual(compat.unpack_calc_result((vals, 2)),(vals,2,''))
        self.assertEqual(compat.unpack_calc_result((vals, 2, '')),(vals,2,''))
        self.assertEqual(compat.unpack_calc_result((vals, 2, 'warning'))[2],'warning')

    def test_invalid_calc_shape_and_values_fail_closed(self):
        vals=(120.,5.,1.,0.,0.,0.)
        for v in [[], (vals,), (vals,2,'','unexpected'), (vals[:5],2),
                  ((float('nan'),5.,1.,0.,0.,0.),2), (vals,2,True), (vals,-1,'failure')]:
            with self.assertRaises(RuntimeError): compat.unpack_calc_result(v)

    def test_house_cusp_index_conversion(self):
        class Fake:
            def __init__(self,modern):self.modern=modern
            def houses_ex(self,*args):
                cusps=tuple(float(i) for i in range(1,13))
                return ((0.,)+cusps if self.modern else cusps),(20.,40.,50.)
        for modern in (False,True):
            cusps,angles=compat.houses_ex(Fake(modern),2451545.,51.,0.,b'P')
            self.assertEqual(cusps,list(map(float,range(1,13))))
            self.assertEqual(angles,(20.,40.,50.))

    def test_deltat_old_and_new(self):
        class Fake:
            def __init__(self,modern):self.modern=modern
            def deltat_ex(self,*args):return (0.0008,'') if self.modern else 0.0008
        self.assertEqual(compat.deltat_ex(Fake(True),2451545.,2),(.0008,''))
        self.assertEqual(compat.deltat_ex(Fake(False),2451545.,2),(.0008,''))

    def test_dual_binding_installation_not_silently_accepted(self):
        with patch('swiss_compat.importlib.metadata.version',return_value='2.10.3.6'):
            with self.assertRaisesRegex(RuntimeError,'Both'):
                compat.installed_binding()

@unittest.skipUnless(core.swe is not None, 'optional Swiss astronomy binding not installed')
class ModernBindingIntegrationTests(unittest.TestCase):
    class ModernProxy:
        def __init__(self,original):self.original=original
        def __getattr__(self,name):return getattr(self.original,name)
        def calc_ut(self,*args):
            position,flags,diagnostic=compat.unpack_calc_result(self.original.calc_ut(*args))
            return position,flags,diagnostic
        def houses_ex(self,*args):
            # Make a modern 13-cusp facade regardless of which ABI is installed.
            raw_cusps,angles=self.original.houses_ex(*args)
            cusps=list(raw_cusps[1:]) if len(raw_cusps)==13 else list(raw_cusps)
            if len(cusps)!=12:
                raise AssertionError('Unexpected real Swiss house array')
            return (0.,)+tuple(cusps),angles
        def deltat_ex(self,*args):
            result=self.original.deltat_ex(*args)
            if isinstance(result,(tuple,list)) and len(result)==2:
                return result
            return result,''

    def options(self):
        return Namespace(datetime='2000-01-01T12:00:00',tz='Europe/London',
             lat=51.4779,lon=0.,fold=None,uncertainty_minutes=0,
             ephemeris='moseph',strict_ephemeris=True,houses='placidus',cross_check=False)

    def test_real_natal_same_with_modern_shape(self):
        legacy=natal.compute(self.options())
        with patch.object(core,'swe',self.ModernProxy(core.swe)):
            modern=natal.compute(self.options())
        self.assertEqual(legacy['chart']['houses'],modern['chart']['houses'])
        self.assertEqual(legacy['chart']['planets'],modern['chart']['planets'])

    def test_real_bazi_same_with_modern_shape(self):
        args=Namespace(datetime='2024-02-10T12:00:00', tz='Asia/Shanghai',
            lat=39.9042, lon=116.4074, fold=None, clock='civil',
            day_boundary='midnight', compare_boundaries=False,
            uncertainty_minutes=0, ephemeris='moseph', strict_ephemeris=True,
            direction='auto', traditional_sex=None, cycles=2)
        legacy=bazi.compute(args)
        with patch.object(core,'swe',self.ModernProxy(core.swe)):
            modern=bazi.compute(args)
        self.assertEqual(legacy['pillars'],modern['pillars'])

    def test_real_solar_terms_same_with_modern_shape(self):
        legacy=solar_terms.calculate(2024,'Asia/Shanghai','moseph',True,False)
        with patch.object(core,'swe',self.ModernProxy(core.swe)):
            modern=solar_terms.calculate(2024,'Asia/Shanghai','moseph',True,False)
        self.assertEqual(legacy['terms'],modern['terms'])

    def test_real_independent_placidus_same_with_modern_shape(self):
        legacy=verify_placidus.compare_case('2000-01-01T12:00:00+00:00',51.4779,0.)
        with patch.object(core,'swe',self.ModernProxy(core.swe)):
            modern=verify_placidus.compare_case('2000-01-01T12:00:00+00:00',51.4779,0.)
        self.assertEqual(legacy,modern)

    def test_simulated_modern_pluto_center_9999_path(self):
        with tempfile.TemporaryDirectory() as folder:
            sat=Path(folder)/'sat';sat.mkdir()
            (sat/'sepm9999.se1').write_bytes(b'\x01'*2048)
            class ModernCenter:
                FLG_SWIEPH, FLG_SPEED = 2, 256
                def set_ephe_path(self, p):self.path=p
                def calc_ut(self, jd, body, flags):
                    assert body == 9999
                    return (251.123, 1.22, 1., 0.,0.,0.), self.FLG_SWIEPH|self.FLG_SPEED,''
            fake=ModernCenter()
            with patch('fetch_horizons.require_engine',return_value=fake):
                r=fetch_horizons.check_swiss_body_center(Path(folder),
                    ('2000-01-01T12:00:00+00:00',))
            self.assertEqual(r['status'],'PASS_SWISS_9999_LOCAL_ONLY')
            self.assertEqual(r['observations'][0]['center_longitude_deg'],251.123)

    def test_real_natal_whole_sign_same_with_modern_shape(self):
        a=self.options();a.houses='whole-sign'
        legacy=natal.compute(a)
        with patch.object(core,'swe',self.ModernProxy(core.swe)):
            modern=natal.compute(a)
        self.assertEqual(legacy['chart']['houses'],modern['chart']['houses'])

if __name__=='__main__':unittest.main()
