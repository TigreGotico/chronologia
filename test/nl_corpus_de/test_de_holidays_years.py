# -*- coding: utf-8 -*-
"""German public holidays with explicit year -- fixed and movable, several
years, gold by an independent computus oracle.

Fixed dates (Neujahr 1-Jan, Tag der Arbeit / "erster Mai" 1-May, Tag der
Deutschen Einheit / "3. Oktober" 3-Oct, Weihnachten 25-Dec) are pure calendar
constants. The movable feasts hang off Western Easter, computed here by the
Anonymous Gregorian algorithm (:func:`_easter`) -- never read from the parser:

    Karfreitag        = Easter - 2      Ostersonntag  = Easter
    Ostermontag       = Easter + 1      Christi H'fahrt = Easter + 39
    Pfingstmontag     = Easter + 50

Each holiday+year names a single day-wide span. Note: the multi-word official
names "Tag der Arbeit" / "Tag der Deutschen Einheit" do NOT compose with a
trailing year (the year wins and the name strands), so this file uses the
everyday numeric forms "erster Mai" and "3. Oktober" -- see
:func:`test_multiword_official_name_plus_year_strands` for the recorded gap.

Anchor 2017-06-27.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, parse


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


_YEARS = range(2016, 2025)

_FIXED = {
    "neujahr": (1, 1),
    "erster mai": (5, 1),
    "3. oktober": (10, 3),
    "weihnachten": (12, 25),
}

_MOVABLE = {
    "karfreitag": -2,
    "ostersonntag": 0,
    "ostermontag": 1,
    "christi himmelfahrt": 39,
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
def test_holiday_year(text, d):
    sp = span(text)
    assert sp.start == AstroDate(d.year, d.month, d.day), f"{text!r} -> {sp}"
    nxt = d + timedelta(days=1)
    assert sp.end == AstroDate(nxt.year, nxt.month, nxt.day)


def test_multiword_official_name_plus_year_binds():
    """The official multi-word name now binds a trailing year (round-2 civil
    holidays): "Tag der Arbeit 2019" resolves to 1 May 2019, just like the
    everyday "erster Mai 2019".
    """
    r = parse("tag der arbeit 2019")
    assert r is not None
    assert r[0].start == AstroDate(2019, 5, 1)
    assert r[1] == ""
    assert span("erster mai 2019").start == AstroDate(2019, 5, 1)
