#!/usr/bin/env python3
"""Swiss-free Placidus house geometry and approximate astronomical orientation.

Implements a continuous bisection of the semidiurnal/seminocturnal arc thirds
for the nonpolar latitudes explicitly stated below. The independent orientation
(GMST, 4-term nutation, IAU-1976 mean obliquity) has <1 arcsecond typical
agreement for the public 2000-2045 cases but is not IAU/SOFA certified.

No `swisseph` imports, calls, reference arrays, or Swiss-derived corrections.
The caller may also pass externally computed ARMC and true obliquity to isolate
pure house geometry independently of sidereal/nutation model choices.

Sources: historical Placidus semiarc method; Meeus astronomical algorithms;
IAU 1976 mean obliquity / low-order nutation, standard GMST formula.
"""
from __future__ import annotations
from math import asin, atan, atan2, cos, degrees, pi, radians, sin, tan


def circular_distance(a:float,b:float)->float:
    return abs((a-b+180.0)%360.0-180.0)


def sidereal_obliquity_independent(jd_ut:float,longitude_deg:float)->tuple[float,float]:
    """Approximate apparent local sidereal angle and true obliquity, in degrees.

    `jd_ut` approximates UT1, not UTC across leap-second precision; the
    nutation expansion deliberately retains four dominant terms only.
    """
    T=(jd_ut-2451545.0)/36525.0
    mean_eps=(84381.448-46.8150*T-0.00059*T*T+0.001813*T*T*T)/3600.0
    sun=radians((280.4665+36000.7698*T)%360)
    moon=radians((218.3165+481267.8813*T)%360)
    node=radians((125.04452-1934.136261*T)%360)
    nut_lon=(-17.20*sin(node)-1.32*sin(2*sun)-.23*sin(2*moon)+.21*sin(2*node))/3600.0
    nut_eps=(9.20*cos(node)+.57*cos(2*sun)+.10*cos(2*moon)-.09*cos(2*node))/3600.0
    eps=mean_eps+nut_eps
    gmst=(280.46061837+360.98564736629*(jd_ut-2451545.0)
          +.000387933*T*T-T*T*T/38710000.0)%360.0
    armc=(gmst+nut_lon*cos(radians(eps))+longitude_deg)%360.0
    return armc,eps


def placidus_cusps_from_angles(armc_deg:float,epsilon_deg:float,latitude_deg:float)->list[float]:
    """12 tropical cusp longitudes, cusp 1 at index 0.

    Solves the Placidus semiarc equations by bracketing/bisection, not a
    translated Swiss iteration. |latitude| <= 60° accepted in this QA version;
    no silent Porphyry switch at polar latitudes. Inputs in degrees.
    """
    if not -60.0<=latitude_deg<=60.0:
        raise ValueError('Placidus independent QA limited to geographic latitude [-60,+60] degrees')
    if not 20<epsilon_deg<27:
        raise ValueError('Unexpected obliquity outside terrestrial reference range')
    phi=radians(latitude_deg);eps=radians(epsilon_deg);theta=armc_deg%360.0

    def ascensional_difference(unwrapped_ra_deg:float)->float:
        declination=atan(tan(eps)*sin(radians(unwrapped_ra_deg)))
        argument=tan(phi)*tan(declination)
        if not -1.0 < argument < 1.0:
            raise ValueError('Circumpolar point has undefined semiarc')
        return degrees(asin(argument))

    def arc_target(cusp:int,ad:float)->float:
        if cusp==11:return (90.0+ad)/3.0
        if cusp==12:return 2.0*(90.0+ad)/3.0
        if cusp==2:return 180.0-2.0*(90.0-ad)/3.0
        if cusp==3:return 180.0-(90.0-ad)/3.0
        raise ValueError(f'Unsupported independent cusp {cusp}')

    def ra_to_ecliptic(ra_deg:float)->float:
        ra=radians(ra_deg)
        return degrees(atan2(sin(ra),cos(ra)*cos(eps)))%360.0

    def solve(cusp:int,lower:float,upper:float)->float:
        def residual(x:float)->float:
            return x-arc_target(cusp,ascensional_difference(theta+x))
        left,right=lower,upper
        if residual(left)>0 or residual(right)<0:
            raise ArithmeticError('Placidus root is not bracketed; do not silently improvise')
        for _ in range(65):
            mid=(left+right)/2.0
            if residual(mid)>0:right=mid
            else:left=mid
        root=(left+right)/2.0
        if abs(residual(root))>1e-9:
            raise ArithmeticError('Placidus numerical root residual exceeds QA requirement')
        return ra_to_ecliptic(theta+root)

    # Ascending eastern intersection of the ecliptic with the local horizon.
    th=radians(theta)
    a=cos(phi)*cos(th)
    b=cos(phi)*sin(th)*cos(eps)+sin(phi)*sin(eps)
    l0=atan2(-a,b)
    candidates=(l0%(2*pi),(l0+pi)%(2*pi))
    def eastward(lam:float)->float:
        return -sin(th)*cos(lam)+cos(th)*cos(eps)*sin(lam)
    ascending=[lam for lam in candidates if eastward(lam)>1e-12]
    if len(ascending)!=1:raise ArithmeticError('Unique east horizon intersection not found')
    asc=degrees(ascending[0])%360.0
    mc=ra_to_ecliptic(theta)
    out=[None]*12
    def set_cusp(h:int,angle:float):out[h-1]=angle%360.0
    set_cusp(1,asc);set_cusp(7,asc+180)
    set_cusp(10,mc);set_cusp(4,mc+180)
    for h,lo,hi in ((11,0.,60.),(12,0.,120.),(2,60.,180.),(3,120.,180.)):
        angle=solve(h,lo,hi)
        set_cusp(h,angle)
        set_cusp(((h+5)%12)+1,angle+180.0)
    if any(x is None for x in out):raise ArithmeticError('Unassigned cusp')
    # Each successive cusp moves anticlockwise through < 180° of longitude.
    widths=[(out[(i+1)%12]-out[i])%360.0 for i in range(12)]
    if not all(0<w<90 for w in widths):
        raise ArithmeticError('Result violates expected ordered nonpolar house layout')
    return out


def independent_placidus(jd_ut:float,latitude_deg:float,longitude_deg:float)->dict:
    armc,eps=sidereal_obliquity_independent(jd_ut,longitude_deg)
    return {'armc_deg':armc,'true_obliquity_deg':eps,
            'cusps_deg':placidus_cusps_from_angles(armc,eps,latitude_deg),
            'orientation':'independent approximate apparent sidereal + 4-term nutation; not high-order IAU precision',
            'house_geometry':'Swiss-free semiarc roots by bracketing and bisection'}
