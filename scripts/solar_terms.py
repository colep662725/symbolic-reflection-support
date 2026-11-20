#!/usr/bin/env python3
"""Calculate 24 solar terms by solar-longitude crossings; offline and reproducible.

Terminology: solar year runs LiChun in year Y to DaHan in year Y+1.
Uses Chinese standard named term order, astronomical longitude in ecliptic of date.
AGPL-3.0-or-later. No astrological outcome predictions.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from calendar_core import require_engine, solar_crossing, sun_longitude, datetime_from_jd, provenance

TERMS=[("立春",315), ("雨水",330), ("惊蛰",345), ("春分",0),
("清明",15), ("谷雨",30), ("立夏",45), ("小满",60),
("芒种",75), ("夏至",90), ("小暑",105), ("大暑",120),
("立秋",135), ("处暑",150), ("白露",165), ("秋分",180),
("寒露",195), ("霜降",210), ("立冬",225), ("小雪",240),
("大雪",255), ("冬至",270), ("小寒",285), ("大寒",300)]

def independent_root_bisection(target,seed,engine,strict):
    """Numerical root code separate from swe.solcross_ut; still same longitude engine."""
    def signed_delta(jd):return ((sun_longitude(jd,engine,strict)-target+180)%360)-180
    left=seed
    fl=signed_delta(left)
    if fl>=0:
        raise RuntimeError("Bisection start must be before the target longitude crossing")
    right=seed+20
    fr=signed_delta(right)
    if fr<=0:
        raise RuntimeError("Could not bracket next solar term in 20 days")
    for _ in range(60):
        mid=(left+right)/2
        if signed_delta(mid)>=0:
            right=mid
        else:
            left=mid
    return (left+right)/2

def calculate(year,timezone,engine='moseph',strict=False,verify_bisection=False):
    s=require_engine()
    if not 1900<=year<=2099:
        raise ValueError("year must be 1900..2099; solar-year terms include next January")
    z=ZoneInfo(timezone)
    jd=s.julday(year,1,25,0,s.GREG_CAL)
    items=[]
    for name,angle in TERMS:
        root,diagnostic=solar_crossing(angle,jd,engine,strict)
        event=datetime_from_jd(root)
        item={"name":name,"target_solar_longitude_deg":angle,
              "utc":event.isoformat(timespec='seconds'),
              "local":event.astimezone(z).isoformat(timespec='seconds'),
              "local_calendar_date":event.astimezone(z).date().isoformat(),
              "numerical_root_check":diagnostic}
        if verify_bisection:
            independently_solved=independent_root_bisection(angle,jd,engine,strict)
            item['bisection_difference_seconds']=round(abs(root-independently_solved)*86400,5)
            if abs(root-independently_solved)*86400 > 60:
                raise RuntimeError("Solar term root and independent bisection implementation disagree by >60 s")
        items.append(item)
        jd=root+1
    _, actual=__import__('calendar_core').calc_planet(s.julday(year,2,15),s.SUN,engine,strict)
    return {"schema_version":"1.3.0","kind":"solar_terms_24",
            "solar_year":year,"iana_timezone":timezone,"terms":items,
            "astronomy":provenance(engine,actual),
            "meaning":"astronomical term crossing, not auspicious-day or fortune prediction",
            "verification_note":"Bisection method uses same solar longitude engine as solcross_ut; NOT an independent ephemeris cross-check. Compare calendar dates with HKO published almanac separately."}

def main(argv=None):
    p=argparse.ArgumentParser(description='24 traditional Chinese solar terms via Sun apparent longitude')
    p.add_argument('--year',type=int,required=True)
    p.add_argument('--tz',default='Asia/Shanghai')
    p.add_argument('--ephemeris',choices=('moseph','swieph'),default='moseph')
    p.add_argument('--strict-ephemeris',action='store_true')
    p.add_argument('--verify-bisection',action='store_true')
    a=p.parse_args(argv)
    try:
        print(json.dumps(calculate(a.year,a.tz,a.ephemeris,a.strict_ephemeris,a.verify_bisection),ensure_ascii=False,indent=2))
    except (RuntimeError, ValueError, KeyError, __import__('zoneinfo').ZoneInfoNotFoundError) as e:
        print(f'solar_terms: {e}',file=sys.stderr)
        return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
