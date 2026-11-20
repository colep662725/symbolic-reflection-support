#!/usr/bin/env python3
"""Independent MODEL-LEVEL comparison of Swiss vs public analytic approximations.

The comparison implements JPL SSD Table 1 separately from Swiss (8 body
longitudes), a truncated lunar harmonic model (Moon), and independent
sidereal/horizon formulas (ASC & MC). It is NOT DE440/JPL Horizons validation.
Pluto & Placidus cusp lengths are NOT independently checked by this tool.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from ephemeris_reference import (
    BODIES, EXCLUDED, jd_from_utc, tropical_longitude_approx,
    independent_asc_mc, angular_distance
)
from swiss_compat import houses_ex as compat_houses_ex, calc_ut as compat_calc_ut
from calendar_core import require_engine, calc_planet

# Pre-declared loose acceptance thresholds in degrees; NOT claimed accuracy.
TOLERANCES_DEG={
    'Sun':.20, 'Moon':.35, 'Mercury':.20,'Venus':.20,'Mars':.25,
    'Jupiter':.45,'Saturn':.50,'Uranus':.20,'Neptune':.20,
    'ASC':.10,'MC':.06
}
PUBLIC_CASES=[
    ('2000-01-01T12:00:00+00:00',51.4779,0.0),
    ('2010-08-15T09:00:00+00:00',40.7128,-74.0060),
    ('2024-06-21T00:00:00+00:00',35.6762,139.6503),
    ('2026-11-20T00:00:00+00:00',-33.8688,151.2093),
    ('2035-04-03T12:00:00+00:00',48.8566,2.3522),
    ('2045-11-08T03:00:00+00:00',13.7563,100.5018),
]

def compare_case(utc_iso:str, lat:float, lon:float)->dict:
    if not -85<=lat<=85 or not -180<=lon<=180:
        raise ValueError('Location outside supported independent QA bounds')
    dt=datetime.fromisoformat(utc_iso)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError('A timezone-aware ISO instant is required')
    dt=dt.astimezone(timezone.utc)
    if not 1800<=dt.year<=2050:
        raise ValueError('JPL Table 1 reference formula restricted to 1800-2050')
    jd=jd_from_utc(dt)
    swe=require_engine()
    results=[]
    actual_engines=set()
    for name in BODIES:
        xx, effective=calc_planet(jd, getattr(swe,name.upper()),'moseph',True)
        actual_engines.add(effective)
        expected=tropical_longitude_approx(name,jd)
        measured=xx[0]%360.0
        diff=angular_distance(expected,measured)
        results.append({'body':name,'swiss_deg':round(measured,7),'independent_reference_deg':round(expected,7),
                        'angular_difference_deg':round(diff,7),'qa_tolerance_deg':TOLERANCES_DEG[name],
                        'pass':diff<=TOLERANCES_DEG[name],
                        'independent_model':'truncated lunar harmonics' if name=='Moon' else 'NASA/JPL SSD approximate Keplerian Table 1'})
    independent_asc,independent_mc=independent_asc_mc(jd,lat,lon)
    _,asp=compat_houses_ex(swe,jd,lat,lon,b'O')
    for name,expected,measured in [('ASC',independent_asc,asp[0]%360),('MC',independent_mc,asp[1]%360)]:
        diff=angular_distance(expected,measured)
        results.append({'body':name,'swiss_deg':round(measured,7),'independent_reference_deg':round(expected,7),
                        'angular_difference_deg':round(diff,7),'qa_tolerance_deg':TOLERANCES_DEG[name],
                        'pass':diff<=TOLERANCES_DEG[name],'independent_model':'mean sidereal time + geometric horizon/meridian'})
    return {'utc':dt.isoformat(timespec='seconds'),'latitude_deg':lat,'longitude_deg':lon,
            'effective_swiss_engine':sorted(actual_engines),
            'checks':results,'count':len(results),'passed':sum(x['pass'] for x in results),
            'status':'PASS_MODEL_LEVEL' if all(x['pass'] for x in results) else 'FAIL_MODEL_LEVEL',
            'not_covered':['Pluto','Placidus/other house cusps','JPL Horizons/DE-series high-accuracy comparison']}

def main(argv=None)->int:
    p=argparse.ArgumentParser(description='Model-level independent ephemeris QA (not DE440/JPL Horizons certification)')
    p.add_argument('--epoch-utc',help='Timezone-aware ISO timestamp, e.g. 2024-06-21T00:00:00+00:00')
    p.add_argument('--lat',type=float,default=35.6762)
    p.add_argument('--lon',type=float,default=139.6503)
    p.add_argument('--strict',action='store_true',help='Exit nonzero if any declared tolerance is exceeded')
    a=p.parse_args(argv)
    try:
        cases=[(a.epoch_utc,a.lat,a.lon)] if a.epoch_utc else PUBLIC_CASES
        data=[compare_case(*case) for case in cases]
        ok=all(x['status']=='PASS_MODEL_LEVEL' for x in data)
        payload={
            'schema_version':'1.3.1','kind':'independent_low_precision_ephemeris_QA',
            'status':'PASS_MODEL_LEVEL' if ok else 'FAIL_MODEL_LEVEL',
            'reference_model':'NASA/JPL SSD published low-accuracy Table 1, truncated lunar harmonics, independent ASC/MC geometry',
            'engine_dependency':'Swiss Ephemeris only for target/output, NOT for reference model',
            'pass_scope':'9/10 natal bodies + ASC + MC per epoch; Pluto omitted; tolerances model-level, NOT arcseconds',
            'dates_tested':len(data),'measurements':sum(c['count'] for c in data),
            'passes':sum(c['passed'] for c in data), 'cases':data,
            'independent_reference_urls':['https://ssd.jpl.nasa.gov/planets/approx_pos.html',
                 'https://github.com/architest/pymeeus/blob/master/pymeeus/Moon.py'],
            'limitations':['This is not an independent JPL Horizons/DE440 comparison.',
                'Moon series is truncated; tropical precession and apparent corrections are approximate.',
                'Pluto has no validated independent model in this release.',
                'Full Placidus cusp geometry is NOT covered.',
                'Even accurate astronomy would not validate predictive astrology.']}
        print(json.dumps(payload,ensure_ascii=False,indent=2))
        return 0 if ok or not a.strict else 1
    except (ValueError,RuntimeError) as exc:
        print(f'verify_ephemeris: {exc}',file=sys.stderr)
        return 2
if __name__=='__main__':raise SystemExit(main())
