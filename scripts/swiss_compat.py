#!/usr/bin/env python3
"""Adapter for legacy pyswisseph and modern pysweph bindings.

This does NOT invent astronomical data or change the selected engine. The C
library has a different Python return ABI across the packages. Normalize it
at ONE boundary and fail for unrecognized results or missing output.
"""
from __future__ import annotations

import importlib.metadata
import math
from collections.abc import Sequence


def installed_binding() -> dict:
    """Return actual Python distribution metadata, not only swe.version."""
    found = []
    for distribution in ('pysweph', 'pyswisseph'):
        try:
            found.append({'name': distribution,
                          'version': importlib.metadata.version(distribution)})
        except importlib.metadata.PackageNotFoundError:
            pass
    if len(found) > 1:
        # Identical swisseph import names make dual installation ambiguous.
        raise RuntimeError('Both pysweph and pyswisseph are installed; uninstall one in this Python environment')
    if found:
        return found[0]
    return {'name': 'unknown', 'version': 'unknown'}


def unpack_calc_result(result) -> tuple[tuple, int, str]:
    """Normalize calc/calc_ut return (xx, flags[, diagnostic])."""
    if not isinstance(result, (tuple, list)) or len(result) not in (2, 3):
        raise RuntimeError('Unsupported swisseph calc result shape (expected 2 or 3 items)')
    values, flags = result[:2]
    message = result[2] if len(result) == 3 else ''
    if not isinstance(values, (tuple, list)) or len(values) != 6:
        raise RuntimeError('Unsupported swisseph positions (expected six coordinates)')
    if not isinstance(flags, int):
        raise RuntimeError('Invalid swisseph return flags')
    if message is None:
        message = ''
    if not isinstance(message, (str, bytes)):
        raise RuntimeError('Unexpected swisseph diagnostic type')
    if isinstance(message, bytes):
        message = message.decode('utf-8', errors='replace')
    if flags < 0:
        raise RuntimeError('Swiss Ephemeris computation error: ' + message)
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in values):
        raise RuntimeError('Swiss Ephemeris returned nonfinite coordinates')
    return tuple(values), flags, message


def calc_ut(swe, jd, body, flags) -> tuple[tuple, int, str]:
    return unpack_calc_result(swe.calc_ut(jd, body, flags))


def houses_ex(swe, jd, latitude, longitude, system) -> tuple[list[float], tuple]:
    raw = swe.houses_ex(jd, latitude, longitude, system)
    if not isinstance(raw, (tuple, list)) or len(raw) != 2:
        raise RuntimeError('Unsupported houses_ex return shape')
    raw_cusps, angles = raw
    if len(raw_cusps) == 12:
        # Legacy: cusps[0] is the first house.
        cusps = list(raw_cusps)
    elif len(raw_cusps) == 13:
        # Modern: cusps[0] is an unused C-style placeholder.
        cusps = list(raw_cusps[1:])
    else:
        raise RuntimeError(f'Unexpected houses_ex cusp count: {len(raw_cusps)}')
    if len(cusps) != 12 or len(angles) < 3:
        raise RuntimeError('Invalid Swiss house geometry')
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in cusps):
        raise RuntimeError('Swiss houses contain nonfinite cusps')
    return cusps, tuple(angles)


def deltat_ex(swe, jd, flags) -> tuple[float, str]:
    result = swe.deltat_ex(jd, flags)
    if isinstance(result, (int, float)):
        return float(result), ''
    if isinstance(result, (tuple, list)) and len(result) == 2:
        value, message = result
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise RuntimeError('Invalid Delta T from Swiss Ephemeris')
        if not isinstance(message, (str, bytes)):
            raise RuntimeError('Invalid Delta T diagnostic')
        if isinstance(message, bytes): message = message.decode('utf-8', errors='replace')
        return float(value), message
    raise RuntimeError('Unsupported deltat_ex result shape')
