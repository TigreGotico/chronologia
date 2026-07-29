# -*- coding: utf-8 -*-
"""Second-pass holiday sweep across decades the original holiday corpus does
NOT touch. ``test_de_holidays_years.py`` covers 2016-2024; this file sweeps
1998-2014 and 2025-2045 (even years, 20 fresh years total) so the two files
never assert the same holiday+year pair.

Fixed dates are calendar constants; two extra everyday names not exercised
by the original file are added here: Heiligabend (Christmas Eve, 24-Dec) and
Silvester (New Year's Eve, 31-Dec). Movable feasts hang off Western Easter,
computed by the Anonymous Gregorian algorithm (:func:`_easter`) -- never
read from the parser -- plus Pfingstsonntag (Easter + 49), one movable feast
the original file omits.

("Aschermittwoch" and "Reformationstag" were probed for this sweep and found
unsupported by the current holiday grammar -- the engine reads them as a
bare year with the holiday name stranded in the remainder -- so they are
left out of this corpus entirely rather than asserted or xfailed; that is a
grammar gap, not a test gap, and is out of scope for a test-only corpus PR.)

Anchor 2017-06-27.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span


def _easter(y):
    a = y % 19
    b, c = y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    ll = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ll) // 451
    mo = (h + ll - 7 * m + 114) // 31
    da = ((h + ll - 7 * m + 114) % 31) + 1
    return date(y, mo, da)


_YEARS = list(range(1998, 2016, 2)) + list(range(2025, 2046, 2))

_FIXED = {
    "neujahr": (1, 1),
    "erster mai": (5, 1),
    "3. oktober": (10, 3),
    "weihnachten": (12, 25),
    "heiligabend": (12, 24),
    "silvester": (12, 31),
}

_MOVABLE = {
    "karfreitag": -2,
    "ostersonntag": 0,
    "ostermontag": 1,
    "christi himmelfahrt": 39,
    "pfingstsonntag": 49,
    "pfingstmontag": 50,
}

_CASES = []
for _y in _YEARS:
    for _name, (_mo, _da) in _FIXED.items():
        _CASES.append((f"{_name} {_y}", date(_y, _mo, _da)))
    _e = _easter(_y)
    for _name, _off in _MOVABLE.items():
        _CASES.append((f"{_name} {_y}", _e + timedelta(days=_off)))


@pytest.mark.parametrize("text,d", _CASES)
def test_holiday_decade_sweep(text, d):
    sp = span(text)
    assert sp.start == AstroDate(d.year, d.month, d.day), f"{text!r} -> {sp}"
    nxt = d + timedelta(days=1)
    assert sp.end == AstroDate(nxt.year, nxt.month, nxt.day)


def test_years_disjoint_from_original_holiday_file():
    assert not (set(_YEARS) & set(range(2016, 2025)))


def test_grid_size_sanity():
    # 20 years x (6 fixed + 6 movable)
    assert len(_CASES) == 20 * 12
