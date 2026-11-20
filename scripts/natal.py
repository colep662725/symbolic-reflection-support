#!/usr/bin/env python3
"""Reproducible tropical western natal astronomical positions (AGPL-3.0-or-later).

This file does not compute an empirically validated personality/fortune prediction.
Swiss Ephemeris: legacy and modern Python bindings supported; Moshier default.
Placidus cusps via Swiss Ephemeris; longitude-between-cusps convention for house.
"""
from __future__ import annotations
import argparse
from datetime import timedelta
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from swiss_compat import houses_ex as compat_houses_ex
from calendar_core import (
    require_engine, parse_birth, julian_ut, julian_day_number_civil, calc_planet,
    in_zodiac, longitude_house, provenance, display_iso, PLANETS, ZODIAC
)


def natal_at(utc, latitude:float, longitude:float, house_system:str, ephemeris:str, strict:bool):
    s=require_engine()
    jd=julian_ut(utc)
    if house_system=='placidus':
        try:
            cusps,aspects=compat_houses_ex(s,jd,latitude,longitude,b'P')
        except s.Error as e:
            raise RuntimeError(f"Placidus houses unavailable at latitude {latitude}: {e}; try --houses whole-sign") from e
        asc,mc=aspects[0],aspects[1]
        # We must not silently switch to Porphyry or whole-sign at high latitudes.
        cusps=list(cusps)
    elif house_system=='whole-sign':
        # Obtain true astronomical ASC, MC independent of the house system.
        # Swiss Ephemeris Porphyry is defined over most latitudes; houses_ex may
        # still fail exactly at poles. Fail with explicit message if it does.
        try:
            _,aspects=compat_houses_ex(s,jd,latitude,longitude,b'O')
        except s.Error as e:
            raise RuntimeError(f"Cannot compute ASC/MC at requested location: {e}") from e
        asc,mc=aspects[0],aspects[1]
        starting_zodiac=int(asc//30)*30.0
        cusps=[(starting_zodiac+30*i)%360.0 for i in range(12)]
    else:
        raise ValueError("House system must be placidus or whole-sign")

    effective_engines=set()
    positions=[]
    for name in PLANETS:
        body=getattr(s,name.upper())
        xx,actual=calc_planet(jd,body,ephemeris,strict)
        effective_engines.add(actual)
        lng=xx[0]%360
        positions.append({"body":name,"longitude_deg":round(lng,8),"latitude_deg":round(xx[1],8),
                          "retrograde":bool(xx[3]<0),"longitude_speed_deg_per_day":round(xx[3],8),
                          "zodiac":in_zodiac(lng),"house":longitude_house(lng,cusps),"effective_ephemeris":actual})
    return {
        "julian_day_ut":round(jd,9),
        "houses": {"system":house_system,"house_membership":"planet longitude lies between consecutive ecliptic cusp longitudes; ignores ecliptic latitude (not swe.house_pos)",
                   "ascendant_deg":round(asc%360,8),"ascendant_zodiac":in_zodiac(asc),
                   "midheaven_deg":round(mc%360,8),"midheaven_zodiac":in_zodiac(mc),
                   "cusps_deg":[round(x%360,8) for x in cusps]},
        "planets":positions,
        "effective_engines":sorted(effective_engines),
    }


def angular_distance(a,b):
    return abs((a-b+180)%360-180)


def compute(args):
    require_engine()
    if not -180<=args.lon<=180 or not -90 < args.lat < 90:
        raise ValueError("Longitude must be -180..180 and latitude strictly between -90 and 90")
    if args.uncertainty_minutes < 0 or args.uncertainty_minutes > 180:
        raise ValueError("uncertainty-minutes must be in 0..180")
    local,utc=parse_birth(args.datetime,args.tz,args.fold)
    chart=natal_at(utc,args.lat,args.lon,args.houses,args.ephemeris,args.strict_ephemeris)
    engines=chart['effective_engines']
    result={"schema_version":"1.3.0","kind":"tropical_natal_chart_calculation",
            "local_datetime":display_iso(local),"utc_datetime":display_iso(utc),
            "iana_timezone":args.tz,"latitude_deg":args.lat,"longitude_deg":args.lon,
            "astronomy":provenance(args.ephemeris,engines[0] if len(engines)==1 else ','.join(engines)),
            "chart":chart,
            "predictions_supported":False,
            "warnings":["The positions describe a reproducible astronomy model; there is no scientific validation of personality or destiny prediction.",
                        "Placidus and whole-sign houses are distinct interpretive conventions; an accurate birth time and location are required for angles.",
                        "No external ephemeris files are bundled; SWIEPH requests may fall back to Moshier unless --strict-ephemeris is set."]}
    if args.cross_check:
        alternative='swieph' if args.ephemeris=='moseph' else 'moseph'
        check=natal_at(utc,args.lat,args.lon,args.houses,alternative,False)
        both=sorted(set(chart['effective_engines']) | set(check['effective_engines']))
        errors=[]
        for original,alternative_position in zip(chart['planets'],check['planets']):
            errors.append({"body":original['body'],"angular_difference_arcsec":round(3600*angular_distance(original['longitude_deg'],alternative_position['longitude_deg']),5)})
        distinct=(set(chart['effective_engines']) != set(check['effective_engines']))
        result['cross_check']={
            "status":"different_analytical_ephemeris_algorithms_in_same_library" if distinct else "NOT_INDEPENDENT_both_calls_used_same_effective_engine",
            "primary_effective_engines":chart['effective_engines'],"alternative_requested":alternative,
            "alternative_effective_engines":check['effective_engines'],
            "max_angular_difference_arcsec":max(x['angular_difference_arcsec'] for x in errors),
            "planet_differences":errors,
            "note":"Even with two distinct engines, this is not an independent library or independent model validation. Reference tests use published calendar/chart fixtures separately."}
    if args.uncertainty_minutes:
        samples=[]
        for mul in (-1,+1):
            t=utc+timedelta(minutes=args.uncertainty_minutes*mul)
            c=natal_at(t,args.lat,args.lon,args.houses,args.ephemeris,args.strict_ephemeris)
            samples.append({"utc":display_iso(t),"local":display_iso(t,local.tzinfo),
                            "ascendant_deg":c['houses']['ascendant_deg'],
                            "midheaven_deg":c['houses']['midheaven_deg'],
                            "planet_houses":{x['body']:x['house'] for x in c['planets']}})
        changed=[body for body in PLANETS if samples[0]['planet_houses'][body]!=samples[1]['planet_houses'][body]]
        result['birth_time_sensitivity']={"plus_minus_minutes":args.uncertainty_minutes,"endpoints":samples,
                                          "endpoint_house_membership_differences":changed,
                                          "warning":"Endpoint test only. Additional crossings within the uncertainty interval may exist."}
    return result


def parser():
    p=argparse.ArgumentParser(description='Verify western natal astronomical positions (not a fate predictor); needs optional Swiss Ephemeris AGPL extra')
    p.add_argument('--datetime',required=True,help='ISO local civil date-time without UTC offset')
    p.add_argument('--tz',required=True,help='IANA timezone, e.g. Europe/London')
    p.add_argument('--lat',type=float,required=True)
    p.add_argument('--lon',type=float,required=True)
    p.add_argument('--fold',type=int,choices=(0,1))
    p.add_argument('--houses',choices=('placidus','whole-sign'),default='placidus')
    p.add_argument('--ephemeris',choices=('moseph','swieph'),default='moseph')
    p.add_argument('--strict-ephemeris',action='store_true')
    p.add_argument('--cross-check',action='store_true')
    p.add_argument('--uncertainty-minutes',type=float,default=0)
    return p


def main(argv=None):
    try:
        a=parser().parse_args(argv)
        print(json.dumps(compute(a),ensure_ascii=False,indent=2))
    except (ValueError,RuntimeError) as exc:
        print(f'natal: {exc}',file=sys.stderr)
        return 2
    return 0
if __name__=='__main__':
    raise SystemExit(main())
