#!/usr/bin/env python3
"""Compare all twelve Swiss Placidus cusps with independent sky geometry.

Two distinct scopes:
  (1) Own sidereal/obliquity orientation + independent Placidus solver
  (2) Swiss-reported ARMC/obliquity + independent Placidus solver
Scope 2 is a **geometry-only** reference, NOT a full independent pipeline.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from placidus_independent import (independent_placidus,placidus_cusps_from_angles,
                                  circular_distance,sidereal_obliquity_independent)
from ephemeris_reference import jd_from_utc
from swiss_compat import houses_ex as compat_houses_ex, calc_ut as compat_calc_ut
from calendar_core import require_engine

PUBLIC_CASES=(
    ('2000-01-01T12:00:00+00:00',51.4779,0.0),
    ('2010-08-15T09:00:00+00:00',40.7128,-74.0060),
    ('2024-06-21T00:00:00+00:00',35.6762,139.6503),
    ('2026-11-20T00:00:00+00:00',-33.8688,151.2093),
    ('2035-04-03T12:00:00+00:00',48.8566,2.3522),
    ('2045-11-08T03:00:00+00:00',13.7563,100.5018),
    ('2024-03-20T12:00:00+00:00',0.0,0.0),
    ('2024-09-22T00:00:00+00:00',58.0,-3.0),
    ('2018-05-14T16:00:00+00:00',-58.0,22.0),
    ('2023-12-22T08:30:00+00:00',60.0,10.0),
    ('2022-07-11T18:30:00+00:00',-60.0,-80.0),
    ('1999-11-11T12:12:00+00:00',24.5,120.0),
)

def compare_case(utc_iso:str,lat:float,lon:float)->dict:
    swe=require_engine()
    dt=datetime.fromisoformat(utc_iso)
    if dt.tzinfo is None:raise ValueError('Timezone-aware public test date required')
    jd=jd_from_utc(dt.astimezone(timezone.utc))
    own=independent_placidus(jd,lat,lon)
    cusps,aspects=compat_houses_ex(swe,jd,lat,lon,b'P')
    swiss_eps=compat_calc_ut(swe,jd,swe.ECL_NUT,swe.FLG_MOSEPH)[0][0]
    same_orientation=placidus_cusps_from_angles(aspects[2],swiss_eps,lat)
    errors=[3600*circular_distance(x,y) for x,y in zip(own['cusps_deg'],cusps)]
    isolated=[3600*circular_distance(x,y) for x,y in zip(same_orientation,cusps)]
    max_full=max(errors)
    max_geom=max(isolated)
    return {'epoch_utc':dt.isoformat(),'latitude_deg':lat,'longitude_deg':lon,
            'cusps_checked':12,'max_full_pipeline_arcsec':round(max_full,8),
            'max_geometry_only_arcsec':round(max_geom,8),
            'orientation_residual_arcsec':round(circular_distance(own['armc_deg'],aspects[2])*3600,8),
            'full_pipeline_pass_2arcsec':max_full<=2.0,
            'geometry_only_pass_0_01arcsec':max_geom<=0.01,
            'max_per_cusp_arcsec':[round(v,6) for v in errors]}

def run(cases=PUBLIC_CASES)->dict:
    results=[compare_case(*case) for case in cases]
    good=all(x['full_pipeline_pass_2arcsec'] and x['geometry_only_pass_0_01arcsec'] for x in results)
    return {'schema_version':'1.3.2','kind':'independent_placidus_cusps_QA',
            'status':'PASS_INDEPENDENT_GEOMETRY_MODEL' if good else 'FAIL_INDEPENDENT_GEOMETRY_MODEL',
            'reference':'independent semiarc-bisection + independent approximate sky orientation',
            'geometry_only_note':'Using Swiss ARMC and obliquity isolates geometry; not independent astronomical orientation',
            'latitude_limit_deg':60,'full_pipeline_tolerance_arcsec':2.0,
            'geometry_only_tolerance_arcsec':0.01,
            'cases':results,'checks':12*len(results),
            'max_full_pipeline_arcsec':round(max(x['max_full_pipeline_arcsec'] for x in results),6),
            'max_geometry_only_arcsec':round(max(x['max_geometry_only_arcsec'] for x in results),6),
            'caveats':['No JPL houses: Placidus is mathematical geometry, not a JPL ephemeris quantity.',
                       'High-latitude (>60 deg), IAU sub-mas sidereal/obliquity, and convention differences unverified.',
                       'Calculation accuracy is unrelated to destiny/astrology predictive validity.']}

def main(argv=None):
    p=argparse.ArgumentParser(description='Independently verify 12 Placidus cusps in moderate latitudes')
    p.add_argument('--strict',action='store_true')
    a=p.parse_args(argv)
    try:
        report=run()
        print(json.dumps(report,ensure_ascii=False,indent=2))
        return 1 if a.strict and not report['status'].startswith('PASS') else 0
    except (ValueError,RuntimeError,ArithmeticError) as e:
        print(f'verify_placidus: {e}',file=sys.stderr)
        return 2
if __name__=='__main__':raise SystemExit(main())
