#!/usr/bin/env python3
"""Verified calendar/pillar data, NOT verified divination (AGPL-3.0-or-later).

Offline bazi calculation for Gregorian dates 1900-2100 using solar term longitude.
Years use LiChun; months use the 12 jie (节), not lunar-month boundaries.
Daily stem anchor verified from public 2000-01-01 and 2024-02-10 calendars.
Explicit late-Zi variants, clock conventions, luck-cycle directions and uncertainty.
"""
from __future__ import annotations

import argparse
from datetime import datetime, date, timedelta, timezone
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from calendar_core import (
    UTC, GANS, ZHIS, JIE, parse_birth, julian_ut, julian_day_number_civil,
    neighboring_jie, jie_boundaries, equation_of_time_minutes, sexagenary,
    provenance, display_iso, require_engine, calc_planet, actual_engine,
)

# 2000-01-01 local civil day is 戊午 (60-cycle ordinal 54); independently verified for 2024-02-10=甲辰.
DAY_ANCHOR_DATE = date(2000, 1, 1)
DAY_ANCHOR_INDEX = 54


def pillar_obj(stem_i:int, branch_i:int) -> dict:
    return {"stem": GANS[stem_i%10], "branch": ZHIS[branch_i%12], "gan_zhi": GANS[stem_i%10]+ZHIS[branch_i%12],
            "stem_index":stem_i%10, "branch_index":branch_i%12}


def daily_index(d:date) -> int:
    delta = julian_day_number_civil(d.year,d.month,d.day)-julian_day_number_civil(2000,1,1)
    return (DAY_ANCHOR_INDEX+delta)%60


def clock_wall_time(local:datetime, utc:datetime, longitude:float, mode:str) -> tuple[datetime,dict]:
    offset_minutes=local.utcoffset().total_seconds()/60.0
    mean_delta=longitude*4.0-offset_minutes
    correction=0.0
    if mode=="apparent-solar":
        correction=equation_of_time_minutes(julian_ut(utc))
    elif mode not in ("civil","mean-solar"):
        raise ValueError("Unknown clock convention")
    total=(mean_delta+correction) if mode!="civil" else 0.0
    shifted=local.replace(tzinfo=None)+timedelta(minutes=total)
    return shifted,{"method":mode,"difference_from_local_clock_minutes":round(total,4),
                    "mean_longitude_correction_minutes":round(mean_delta,4),
                    "equation_of_time_minutes":round(correction,4),
                    "warning":"The official clock is the civil clock; mean/apparent solar time is an optional school convention, not a standardized BaZi requirement."}


def chart_at(local:datetime, utc:datetime, longitude:float, day_boundary:str, clock_mode:str, engine:str, strict:bool=False):
    if day_boundary not in ("midnight", "zi-start", "split-zi"):
        raise ValueError("day boundary must be midnight, zi-start or split-zi")
    jd=julian_ut(utc)
    wall,correction=clock_wall_time(local,utc,longitude,clock_mode)
    actualyear=utc.astimezone(local.tzinfo).year
    lichun=jie_boundaries(actualyear,engine,strict)[0]
    y=actualyear if jd>=lichun['jd_ut'] else actualyear-1
    year_i=(y-1984)%60
    year= pillar_obj(year_i%10,year_i%12)
    previous,nxt=neighboring_jie(jd,actualyear,engine,strict)
    jie_i=next(i for i,(name,_) in enumerate(JIE) if name==previous['name'])
    # 甲/己 years: 寅 month is 丙寅; successive jie advance one stem & branch.
    month_stem_i=((year_i%10)%5*2+2+jie_i)%10
    month_branch_i=(2+jie_i)%12
    month=pillar_obj(month_stem_i,month_branch_i)
    current_day=wall.date()
    after_23=wall.hour==23
    # split-zi: calendar day stays the same, but Zi-hour stem is computed from the following day's stem.
    day_date=current_day+timedelta(days=1) if after_23 and day_boundary=="zi-start" else current_day
    hour_date=current_day+timedelta(days=1) if after_23 and day_boundary in ("zi-start","split-zi") else current_day
    day_index=daily_index(day_date)
    hour_day_index=daily_index(hour_date)
    hour_branch_index=((wall.hour+1)//2)%12
    hour_stem_index=((hour_day_index%10)%5*2+hour_branch_index)%10
    result={
        "year":year,"month":month,
        "day":pillar_obj(day_index%10,day_index%12),
        "hour":pillar_obj(hour_stem_index,hour_branch_index),
        "eight_characters":"".join([year['gan_zhi'],month['gan_zhi'],pillar_obj(day_index%10,day_index%12)['gan_zhi'],pillar_obj(hour_stem_index,hour_branch_index)['gan_zhi']]),
        "day_master":GANS[day_index%10],
        "basis":{
            "year_boundary":"LiChun solar longitude 315° (year changes at instant, not on Lunar New Year)",
            "month_boundary":"12 jie solar longitude boundaries (month changes at instant)",
            "day_boundary":day_boundary,"clock":correction,
            "day_anchor":"2000-01-01=戊午 (independently cross-checked with 2024-02-10=甲辰)",
            "year_number":y,"day_date_used":day_date.isoformat(),"hour_stem_day_used":hour_date.isoformat(),
            "previous_jie":{"name":previous['name'],"utc":previous['utc'],"sun_longitude_deg":previous['angle_deg']},
            "next_jie":{"name":nxt['name'],"utc":nxt['utc'],"sun_longitude_deg":nxt['angle_deg']},
            "lichun_utc":lichun['utc'],
        }
    }
    return result, previous, nxt


def luck_cycles(local:datetime,utc:datetime,chart:dict, previous:dict, next_event:dict, direction:str, count:int=8)->dict:
    if direction not in ("forward", "backward"):
        raise ValueError("direction must be forward/backward")
    if not 1<=count<=12:
        raise ValueError("count must be 1..12")
    jd=julian_ut(utc)
    event=next_event if direction=="forward" else previous
    elapsed_days=abs(event['jd_ut']-jd)
    # Conventional rule: 3 solar days -> 1 nominal year; use 365.2425d/year for display only.
    nominal_years=elapsed_days/3.0
    cycle_start=utc+timedelta(days=nominal_years*365.2425)
    m=chart['month']
    step=1 if direction=="forward" else -1
    cycles=[]
    for k in range(1,count+1):
        beginning=cycle_start+timedelta(days=(k-1)*10*365.2425)
        end=cycle_start+timedelta(days=k*10*365.2425)
        cycles.append({"number":k,"gan_zhi":pillar_obj(m['stem_index']+step*k,m['branch_index']+step*k)['gan_zhi'],
                       "start_age_nominal_years":round(nominal_years+(k-1)*10,2),
                       "end_age_nominal_years":round(nominal_years+k*10,2),
                       "start_local_approx_date":beginning.astimezone(local.tzinfo).date().isoformat(),
                       "end_local_approx_date":end.astimezone(local.tzinfo).date().isoformat()})
    return {
        "direction":direction,
        "reference_jie":{"name":event['name'],"utc":event['utc']},
        "birth_to_jie_solar_days":round(elapsed_days,8),
        "start_age_nominal_years":round(nominal_years,4),
        "start_local_approx_date":cycle_start.astimezone(local.tzinfo).date().isoformat(),
        "method":"3 true solar days per nominal year, 365.2425-day display year; different traditional conversion conventions can shift age/date",
        "status":"conventional approximate start (not exact civil-date theorem)",
        "cycles":cycles,
    }


def resolve_direction(requested:str, traditional_sex:str|None, chart:dict)->str|None:
    if requested in ("forward","backward"):
        return requested
    if requested!="auto":
        raise ValueError("direction must be auto, forward or backward")
    if not traditional_sex:
        return None
    if traditional_sex not in ("male","female"):
        raise ValueError("traditional sex parameter must be male or female")
    yang_year=(chart['year']['stem_index']%2==0)
    return "forward" if ((traditional_sex=="male") == yang_year) else "backward"


def compute(args)->dict:
    require_engine()
    if not -180<=args.lon<=180 or not -90<=args.lat<=90:
        raise ValueError("Longitude must be -180..180 and latitude -90..90")
    local,utc=parse_birth(args.datetime,args.tz,args.fold)
    base,prev,nxt=chart_at(local,utc,args.lon,args.day_boundary,args.clock,args.ephemeris,args.strict_ephemeris)
    direction=resolve_direction(args.direction,args.traditional_sex,base)
    result={"schema_version":"1.3.0","kind":"bazi_calculation","local_datetime":display_iso(local),
            "utc_datetime":display_iso(utc),"latitude_deg":args.lat,"longitude_deg":args.lon,
            "iana_timezone":args.tz,"pillars":base,
            "astronomy":provenance(args.ephemeris, calc_planet(julian_ut(utc),require_engine().SUN,args.ephemeris,args.strict_ephemeris)[1]),
            "predictions_supported":False,
            "uncertainties":["Traditional rules vary; in particular the late-Zi day boundary and apparent-solar-time convention are not universally agreed.",
                             "Birth time and geographic inputs must be user-verified; municipal coordinates are only reference points.",
                             "Solar-term crossing times are model computations, not official Chinese calendar announcements."]}
    if direction:
        result['luck_cycles']=luck_cycles(local,utc,base,prev,nxt,direction,args.cycles)
        result['luck_cycles']['direction_source']="explicit" if args.direction!='auto' else "traditional_year_yin_yang_and_user_supplied_sex_parameter"
    else:
        result['luck_cycles']={"status":"not computed; supply --direction or --traditional-sex; no sex/identity inferred"}
    if args.compare_boundaries:
        result['boundary_comparison']={}
        for policy in ('midnight','zi-start','split-zi'):
            ch,_,_=chart_at(local,utc,args.lon,policy,args.clock,args.ephemeris,args.strict_ephemeris)
            result['boundary_comparison'][policy]={"eight_characters":ch['eight_characters'],"day_master":ch['day_master']}
    if args.uncertainty_minutes:
        if not 0<=args.uncertainty_minutes<=180:
            raise ValueError("uncertainty-minutes must be in 0..180")
        variants=[]
        for sign in [-1,1]:
            t=utc+timedelta(minutes=sign*args.uncertainty_minutes)
            l=t.astimezone(local.tzinfo)
            ch,_,_=chart_at(l,t,args.lon,args.day_boundary,args.clock,args.ephemeris,args.strict_ephemeris)
            variants.append({"utc":display_iso(t),"local":display_iso(l),"eight_characters":ch['eight_characters']})
        result['birth_time_sensitivity']={"plus_minus_minutes":args.uncertainty_minutes,"endpoint_charts":variants,
            "warning":"Endpoints are examples, not a proof that all intervening values are the same; near jie or hour boundaries evaluate more points."}
    return result


def make_parser():
    p=argparse.ArgumentParser(description="Verifiable astronomical BaZi pillars and conventional luck-cycle arithmetic. NO predictions. Requires pyswisseph (AGPL).")
    p.add_argument('--datetime',required=True,help='ISO local civil birth time (no offset), e.g. 2024-02-10T23:45:00')
    p.add_argument('--tz',required=True,help='IANA timezone e.g. Asia/Shanghai')
    p.add_argument('--lat',type=float,required=True,help='geographic latitude north-positive')
    p.add_argument('--lon',type=float,required=True,help='geographic longitude east-positive')
    p.add_argument('--fold',type=int,choices=(0,1),help='DST ambiguous-time fold (only when necessary)')
    p.add_argument('--clock',choices=('civil','mean-solar','apparent-solar'),default='civil')
    p.add_argument('--day-boundary',choices=('midnight','zi-start','split-zi'),default='midnight')
    p.add_argument('--compare-boundaries',action='store_true')
    p.add_argument('--uncertainty-minutes',type=float,default=0)
    p.add_argument('--ephemeris',choices=('moseph','swieph'),default='moseph')
    p.add_argument('--strict-ephemeris',action='store_true')
    p.add_argument('--direction',choices=('auto','forward','backward'),default='auto')
    p.add_argument('--traditional-sex',choices=('male','female'),help='only for customary direction; explicit alternative --direction is available')
    p.add_argument('--cycles',type=int,default=8)
    return p


def main(argv=None):
    try:
        args=make_parser().parse_args(argv)
        print(json.dumps(compute(args),ensure_ascii=False,indent=2))
    except (ValueError, RuntimeError) as exc:
        print(f"bazi: {exc}",file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
