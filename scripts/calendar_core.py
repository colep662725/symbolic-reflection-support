"""Astronomical calculation primitives for v1.3 (AGPL-3.0-or-later).

Supports pyswisseph 2.10.3.2 and pysweph >=2.10.3.6 through swiss_compat; never guesses.
Swiss Ephemeris is dual-licensed AGPL/professional. The project selects AGPL.
No network requests or stored birth profiles. Gregorian civil calendar, 1900–2100.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import warnings
from swiss_compat import calc_ut as compat_calc_ut, installed_binding

try:
    import swisseph as swe
except ImportError:
    swe = None

UTC = timezone.utc
GANS = "甲乙丙丁戊己庚辛壬癸"
ZHIS = "子丑寅卯辰巳午未申酉戌亥"
JIE = [
    ("立春", 315.0), ("惊蛰", 345.0), ("清明", 15.0),
    ("立夏", 45.0), ("芒种", 75.0), ("小暑", 105.0),
    ("立秋", 135.0), ("白露", 165.0), ("寒露", 195.0),
    ("立冬", 225.0), ("大雪", 255.0), ("小寒", 285.0),
]
ZODIAC = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]


def require_engine():
    if swe is None:
        raise RuntimeError("Astronomy extra missing. Install: python -m pip install -r requirements-astronomy.txt. Calculation aborted (no invented values).")
    if getattr(swe, "version", "") != "2.10.03":
        # Keep runtime version visible to user rather than concealing differences.
        pass
    return swe


def parse_birth(iso_local: str, iana_timezone: str, fold: int | None = None) -> tuple[datetime, datetime]:
    """Return IANA local civil time and corresponding UTC instant; reject DST gaps/overlaps."""
    try:
        d = datetime.fromisoformat(iso_local)
        if d.tzinfo is not None:
            raise ValueError("Use a local datetime WITHOUT offset and provide --tz explicitly")
        if not 1900 <= d.year <= 2100:
            raise ValueError("v1.3 supports Gregorian dates 1900–2100 only")
        z = ZoneInfo(iana_timezone)
    except ZoneInfoNotFoundError as e:
        raise ValueError("Unknown timezone or missing system tzdata; install package tzdata and use IANA zone e.g. Asia/Shanghai") from e
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid birth date/time or timezone: {e}") from e
    def offset_of(f):
        loc = d.replace(tzinfo=z, fold=f)
        utc = loc.astimezone(UTC)
        reverse = utc.astimezone(z)
        return loc, utc, reverse.replace(tzinfo=None) == d
    a = offset_of(0)
    b = offset_of(1)
    if not a[2] and not b[2]:
        raise ValueError("Civil local time does not exist due to DST/timezone transition")
    ambiguous = a[2] and b[2] and a[1] != b[1]
    if ambiguous and fold is None:
        raise ValueError("Ambiguous DST civil time: specify --fold 0 or --fold 1")
    if fold not in (None, 0, 1):
        raise ValueError("--fold must be 0 or 1")
    selected = b if fold == 1 else a
    if not selected[2]:
        raise ValueError("Specified fold maps to a nonexistent local clock reading")
    return selected[0], selected[1]


def julian_ut(when_utc: datetime) -> float:
    s = require_engine()
    t = when_utc.astimezone(UTC)
    h = t.hour + t.minute/60.0 + (t.second + t.microsecond/1e6)/3600.0
    return s.julday(t.year, t.month, t.day, h, s.GREG_CAL)


def datetime_from_jd(jd: float) -> datetime:
    s = require_engine()
    year, month, day, decimal_hour = s.revjul(jd, s.GREG_CAL)
    return datetime(year, month, day, tzinfo=UTC) + timedelta(hours=decimal_hour)


def engine_flag(requested: str) -> int:
    s = require_engine()
    if requested not in ("moseph", "swieph"):
        raise ValueError("ephemeris must be moseph or swieph")
    return s.FLG_MOSEPH if requested == "moseph" else s.FLG_SWIEPH


def actual_engine(return_flags: int) -> str:
    s = require_engine()
    if return_flags & s.FLG_JPLEPH:
        return "jpleph"
    if return_flags & s.FLG_SWIEPH:
        return "swieph"
    if return_flags & s.FLG_MOSEPH:
        return "moseph"
    return "unreported"


def calc_planet(jd: float, body: int, requested: str = "moseph", strict: bool = False):
    s = require_engine()
    position, flags, diagnostic = compat_calc_ut(s, jd, body, engine_flag(requested) | s.FLG_SPEED)
    effective = actual_engine(flags)
    if diagnostic.strip():
        warnings.warn("Swiss Ephemeris: " + diagnostic.strip(), RuntimeWarning, stacklevel=2)
    if strict and effective != requested:
        raise RuntimeError(f"Requested {requested}, but actual engine {effective}; ephemeris files may be unavailable")
    return position, effective


def sun_longitude(jd: float, requested: str = "moseph", strict: bool = False) -> float:
    s = require_engine()
    return calc_planet(jd, s.SUN, requested, strict)[0][0] % 360.0


def solar_crossing(angle: float, jd_start: float, engine: str = "moseph", strict: bool = False) -> tuple[float, dict]:
    """Next apparent tropical Sun longitude crossing after a UT Julian day."""
    s = require_engine()
    jd = s.solcross_ut(angle % 360.0, jd_start, engine_flag(engine))
    if jd < jd_start - 1e-8:
        raise RuntimeError("Solar longitude crossing search failed")
    longitude = sun_longitude(jd, engine, strict)
    angular_error = abs((longitude - angle + 180.0) % 360.0 - 180.0)
    if angular_error > 0.002:  # ~3 minutes of solar time; unexpected algorithm mismatch
        raise RuntimeError(f"Solar crossing cannot be verified: longitude mismatch {angular_error} degrees")
    return jd, {"sun_longitude_deg": round(longitude, 8), "residual_arcsec": round(angular_error*3600, 5), "verification_method": "re-evaluate solar longitude at returned root (same Swiss library, not independent engine)"}


def jie_boundaries(year: int, engine: str = "moseph", strict: bool = False) -> list[dict]:
    """12 month-start solar terms in chronological order from LiChun of Gregorian year."""
    s = require_engine()
    if not 1899 <= year <= 2101:
        raise ValueError("solar boundary year out of supported range (1899-2101)")
    out = []
    # Start before LiChun. Each forward search starts after preceding term, before next.
    jd = s.julday(year, 1, 25, 0, s.GREG_CAL)
    for name, angle in JIE:
        cross, check = solar_crossing(angle, jd, engine, strict)
        out.append({"name": name, "angle_deg": angle, "utc": datetime_from_jd(cross).isoformat(timespec="seconds"), "jd_ut": cross, "check": check})
        jd = cross + 1.0
    return out


def neighboring_jie(jd: float, year: int, engine: str = "moseph", strict: bool = False):
    all_events = []
    for y in (year-1, year, year+1):
        if 1899 <= y <= 2101:
            all_events.extend(jie_boundaries(y, engine, strict))
    all_events.sort(key=lambda e:e['jd_ut'])
    prev = [x for x in all_events if x['jd_ut'] <= jd]
    nxt = [x for x in all_events if x['jd_ut'] > jd]
    if not prev or not nxt:
        raise RuntimeError("No surrounding jie solar term in restricted calendar range")
    return prev[-1], nxt[0]


def equation_of_time_minutes(jd: float) -> float:
    return require_engine().time_equ(jd)*1440.0


def display_iso(dt: datetime, tz=None) -> str:
    if tz is not None:
        dt = dt.astimezone(tz)
    return dt.isoformat(timespec="seconds")


def julian_day_number_civil(y: int, m: int, d: int) -> int:
    """Integer JDN for proleptic Gregorian local civil DATE (not astronomical time)."""
    a = (14-m)//12
    yy = y+4800-a
    mm = m+12*a-3
    return d+(153*mm+2)//5+365*yy+yy//4-yy//100+yy//400-32045


def sexagenary(n: int) -> str:
    return GANS[n%10]+ZHIS[n%12]


def in_zodiac(degree: float):
    v = degree % 360.0
    return {"sign_en":ZODIAC[int(v//30)],"sign_index":int(v//30),"degree_in_sign":round(v%30,6)}


def longitude_house(longitude: float, cusps: list[float]) -> int:
    """Longitude-between-adjacent-cusps convention, not latitude-adjusted 3D house_pos."""
    x = longitude%360.0
    for i in range(12):
        beg = cusps[i]%360.0
        end = cusps[(i+1)%12]%360.0
        if (x-beg)%360.0 < (end-beg)%360.0:
            return i+1
    raise RuntimeError("Could not assign house, possibly invalid polar house cusps")


def provenance(engine: str, effective: str | None = None):
    s=require_engine()
    binding = installed_binding()
    return {
        "library":"Swiss Ephemeris Python binding",
        "python_binding_installed":binding,
        "library_version":s.version,
        "python_binding_supported":["pyswisseph==2.10.3.2", "pysweph==2.10.3.6"],
        "requested_ephemeris":engine,
        "effective_ephemeris":effective,
        "ephemeris_data_bundled":False,
        "tropical":True,
        "positions":"geocentric apparent ecliptic of date; longitude degrees",
        "time_scale":"UTC input approximated as UT1 (error usually below arcsecond; not a navigation-grade result)",
        "license":"AGPL-3.0-or-later for this package and the optional pyswisseph engine; Swiss commercial license alternative requires separate agreement",
        "offline":True,
    }
