#!/usr/bin/env python3
"""INDEPENDENT, LOW-PRECISION reference for ephemeris QA (AGPL-3.0-or-later).

No imports from swisseph, natal or calendar_core. Position calculations
are based on NASA/JPL SSD's public approximate Keplerian element Table 1,
valid 1800--2050 CE, transformed to approximate geocentric ecliptic-of-date.
Moon uses a separately coded truncated Meeus-style lunar series.
ASC / MC use elementary horizon geometry plus a separate sidereal-time formula.

THIS IS NOT DE440/Horizons, NOT A SUB-ARCMINUTE CERTIFICATE. Apparent vs geometric,
EM barycenter vs geocenter, simple precession/nutation and light-time differences
are deliberately retained and covered by loose QA tolerances. Pluto omitted:
not included in current JPL Table 1. It must not be marked as validated.

Sources:
https://ssd.jpl.nasa.gov/planets/approx_pos.html
https://github.com/architest/pymeeus/blob/master/pymeeus/Moon.py
https://ssd.jpl.nasa.gov/horizons/manual.html
"""
from __future__ import annotations
from datetime import datetime, timezone
from math import sin, cos, sqrt, atan2, radians, degrees, pi

# JPL Table 1: epoch elements (a,e,I,L,perihelion,ascending node) and per-century rates.
# Independent numerical implementation; coefficients are astronomic numeric facts.
ELEMENTS = {
    'Mercury': ((.38709927,.20563593,7.00497902,252.25032350,77.45779628,48.33076593),
                (.00000037,.00001906,-.00594749,149472.67411175,.16047689,-.12534081)),
    'Venus': ((.72333566,.00677672,3.39467605,181.97909950,131.60246718,76.67984255),
              (.00000390,-.00004107,-.00078890,58517.81538729,.00268329,-.27769418)),
    'EM_Bary': ((1.00000261,.01671123,-.00001531,100.46457166,102.93768193,0.),
                (.00000562,-.00004392,-.01294668,35999.37244981,.32327364,0.)),
    'Mars': ((1.52371034,.09339410,1.84969142,-4.55343205,-23.94362959,49.55953891),
             (.00001847,.00007882,-.00813131,19140.30268499,.44441088,-.29257343)),
    'Jupiter': ((5.20288700,.04838624,1.30439695,34.39644051,14.72847983,100.47390909),
                (-.00011607,-.00013253,-.00183714,3034.74612775,.21252668,.20469106)),
    'Saturn': ((9.53667594,.05386179,2.48599187,49.95424423,92.59887831,113.66242448),
               (-.00125060,-.00050991,.00193609,1222.49362201,-.41897216,-.28867794)),
    'Uranus': ((19.18916464,.04725744,.77263783,313.23810451,170.95427630,74.01692503),
               (-.00196176,-.00004397,-.00242939,428.48202785,.40805281,.04240589)),
    'Neptune': ((30.06992276,.00859048,1.77004347,-55.12002969,44.96476227,131.78422574),
                (.00026291,.00005105,.00035372,218.45945325,-.32241464,-.00508664)),
}
BODIES = ('Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune')
EXCLUDED = ('Pluto',)

def jd_from_utc(when:datetime)->float:
    if when.tzinfo is None or when.utcoffset() is None:
        raise ValueError('UTC-aware datetime required')
    return 2440587.5 + when.astimezone(timezone.utc).timestamp()/86400.0

def _hvector(body:str, T:float)->tuple[float,float,float]:
    initial, slope=ELEMENTS[body]
    a,e,I,L,peri,node=(v+s*T for v,s in zip(initial,slope))
    anomaly=radians((L-peri)%360)
    E=anomaly
    for _ in range(30):
        delta=(anomaly-E+e*sin(E))/(1-e*cos(E))
        E+=delta
        if abs(delta)<1e-14:break
    else:
        raise ArithmeticError('Kepler solver did not converge')
    X=a*(cos(E)-e); Y=a*sqrt(1-e*e)*sin(E)
    w=radians(peri-node); n=radians(node); inc=radians(I)
    return (
        (cos(w)*cos(n)-sin(w)*sin(n)*cos(inc))*X+(-sin(w)*cos(n)-cos(w)*sin(n)*cos(inc))*Y,
        (cos(w)*sin(n)+sin(w)*cos(n)*cos(inc))*X+(-sin(w)*sin(n)+cos(w)*cos(n)*cos(inc))*Y,
        sin(w)*sin(inc)*X+cos(w)*sin(inc)*Y,
    )

def moon_approximate_longitude(jd:float)->float:
    """Truncated classical lunar harmonics; accuracy intentionally coarse."""
    T=(jd-2451545.0)/36525.0
    mean_l=218.3164477+(481267.88123421+(-.0015786+(1/538841-T/65194000)*T)*T)*T
    D=radians((297.8501921+(445267.1114034+(-.0018819+(1/545868-T/113065000)*T)*T)*T)%360)
    ms=radians((357.5291092+(35999.0502909+(-.0001536+T/24490000)*T)*T)%360)
    mm=radians((134.9633964+(477198.8675055+(.0087414+(1/69699-T/14712000)*T)*T)*T)%360)
    F=radians((93.2720950+(483202.0175233+(-.0036539+(-1/3526000+T/863310000)*T)*T)*T)%360)
    corr=(6.289*sin(mm)+1.274*sin(2*D-mm)+.658*sin(2*D)+.214*sin(2*mm)
          -.186*sin(ms)-.114*sin(2*F)+.059*sin(2*D-2*mm)
          +.057*sin(2*D-ms-mm)+.053*sin(2*D+mm)+.046*sin(2*D-ms)+.041*sin(ms-mm))
    return (mean_l+corr)%360.0

def tropical_longitude_approx(body:str, jd:float)->float:
    if not 2378496.5 <= jd <= 2470172.5: # approx 1800-2050; explicitly don't extrapolate
        raise ValueError('JPL Table 1 approximation only supported for 1800--2050')
    if body=='Moon':return moon_approximate_longitude(jd)
    if body not in ('Sun',*ELEMENTS.keys()) or body=='EM_Bary':
        raise ValueError('Unsupported comparison body (Pluto is NOT verified)')
    T=(jd-2451545.0)/36525.0
    earth=_hvector('EM_Bary',T)
    xyz=(0.,0.,0.) if body=='Sun' else _hvector(body,T)
    x,y,z=(v-e for v,e in zip(xyz,earth))
    l_j2000=degrees(atan2(y,x))%360
    # First-order mean equinox precession of longitude from J2000 to date;
    # no full aberration, nutation, light-time, Earth/Moon split correction.
    return (l_j2000+1.3970*T+0.00031*T*T)%360

def independent_asc_mc(jd:float, latitude_deg:float, longitude_deg:float)->tuple[float,float]:
    """Mean sidereal angle and geometric east horizon/meridian intersection.

    Does NOT use Swiss houses/ayanamsa or Placidus cusp calculations.
    Not reliable at geographical poles or horizon-degenerate epochs.
    """
    if not -85<=latitude_deg<=85:
        raise ValueError('Independent angle comparison restricted to latitude -85..85')
    T=(jd-2451545.0)/36525.0
    theta=radians((280.46061837+360.98564736629*(jd-2451545.0)
                   +.000387933*T*T-T*T*T/38710000+longitude_deg)%360)
    phi=radians(latitude_deg)
    eps=radians(23.439291111-.013004167*T)
    A=cos(phi)*cos(theta)
    B=cos(phi)*sin(theta)*cos(eps)+sin(phi)*sin(eps)
    l0=atan2(-A,B)
    candidates=(l0%(2*pi), (l0+pi)%(2*pi))
    east=lambda angle: -sin(theta)*cos(angle)+cos(theta)*cos(eps)*sin(angle)
    asc=candidates[0] if east(candidates[0])>0 else candidates[1]
    if abs(east(asc))<1e-8:raise ValueError('Ascendant horizon degeneracy')
    mc=atan2(sin(theta)/cos(eps),cos(theta))%(2*pi)
    return (degrees(asc), degrees(mc))

def angular_distance(a:float,b:float)->float:
    return abs((a-b+180)%360-180)
