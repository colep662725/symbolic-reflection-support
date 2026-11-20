#!/usr/bin/env python3
"""Compare independently OBTAINED JPL Horizons #31 reference observations.

This module only reads local user-supplied JSON; no network is used and we DO
NOT claim to have authenticated its provenance. It never generates Horizons
values from Swiss positions. Genuine high-precision independent checking
requires the user to download actual JPL Horizons results first.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from ephemeris_reference import angular_distance,jd_from_utc
from calendar_core import require_engine,calc_planet

ALLOWED={"Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"}

def compare(payload:dict,tolerance_arcsec:float=30.0)->dict:
    if not 0<tolerance_arcsec<=3600:raise ValueError('tolerance_arcsec must be (0,3600]')
    meta=payload.get('metadata',{})
    if meta.get('center')!='500@399' or str(meta.get('quantity'))!='31':
        raise ValueError('Require JPL Horizons geocentric center=500@399 and Observer Quantity=31')
    if meta.get('coordinate_type')!='observer_ecliptic_of_date_apparent':
        raise ValueError('Only observer apparent ecliptic of date may be compared')
    if meta.get('time_scale') not in ('UTC','UT'):
        raise ValueError('Require explicit UTC or UT time scale')
    if not payload.get('observations'):
        raise ValueError('No observed ephemeris data provided; do not invent a reference')
    swe=require_engine()
    checked=[]
    for obs in payload['observations']:
        body=obs['body']
        if body not in ALLOWED:raise ValueError(f'Unsupported body {body}')
        dt=datetime.fromisoformat(obs['utc'])
        if dt.tzinfo is None or dt.utcoffset() is None:raise ValueError('Require aware UTC epoch')
        dt=dt.astimezone(timezone.utc)
        ref=float(obs['longitude_deg'])
        if not 0<=ref<360:raise ValueError('Longitude must be [0,360)')
        sw,engine=calc_planet(jd_from_utc(dt),getattr(swe,body.upper()),'moseph',True)
        error=angular_distance(sw[0]%360,ref)*3600
        checked.append({'body':body,'utc':dt.isoformat(timespec='seconds'),
                        'reference_deg':ref,'moseph_deg':round(sw[0]%360,8),
                        'difference_arcsec':round(error,4),'tolerance_arcsec':tolerance_arcsec,
                        'pass':error<=tolerance_arcsec})
    status='PASS_USER_SUPPLIED_FIXTURE' if all(x['pass'] for x in checked) else 'FAIL_USER_SUPPLIED_FIXTURE'
    return {'schema_version':'1.3.1','kind':'provided_reference_ephemeris_comparison',
            'status':status,'observations':checked,'count':len(checked),
            'passes':sum(x['pass'] for x in checked),
            'provenance':'USER_SUPPLIED_NOT_AUTHENTICATED',
            'source_claimed_by_user':meta.get('source_description','unspecified'),
            'note':'This checks given positions numerically but does not prove that the input file came from NASA/JPL. Must retain source query/export for audit.',
            'limitations':'Reference frame, TT/UT and angular conventions must match; fine accuracy is not guaranteed by this comparison.'}

def main(argv=None):
    p=argparse.ArgumentParser(description='Compare a LOCAL, manually verified JPL Horizons #31 JSON fixture')
    p.add_argument('--file',type=Path,required=True)
    p.add_argument('--tolerance-arcsec',type=float,default=30)
    p.add_argument('--strict',action='store_true')
    args=p.parse_args(argv)
    try:
        data=json.loads(args.file.read_text(encoding='utf-8'))
        report=compare(data,args.tolerance_arcsec)
        print(json.dumps(report,ensure_ascii=False,indent=2))
        return 0 if report['status'].startswith('PASS') or not args.strict else 1
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print(f'compare_horizons_fixture: {exc}',file=sys.stderr)
        return 2
if __name__=='__main__':raise SystemExit(main())
