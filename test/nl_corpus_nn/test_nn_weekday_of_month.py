"""nn: ordinal-weekday-of-month and last-weekday-of-month, explicit year.

Surface: ``<ordinal> <weekday> i <month> <year>`` (indefinite weekday form),
e.g. ``tredje måndag i mars 2020`` -> the 3rd Monday of March 2020.  The
"last" variant uses ``siste``.  Gold is computed by independent calendar
arithmetic (calendar module), never pinned from the engine.

NOTE (divergence, not tested here): the *definite* weekday form with the -en
suffix (``tredje måndagen i mars``) does NOT resolve to the nth weekday -- it
collapses to the whole month.  Only the indefinite form is exercised.
"""
import calendar
from datetime import datetime, timedelta

import pytest

from ._corpus import parse, AstroDate

MONTHS = {1: 'januar', 2: 'februar', 3: 'mars', 4: 'april', 5: 'mai',
          6: 'juni', 7: 'juli', 8: 'august', 9: 'september', 10: 'oktober',
          11: 'november', 12: 'desember'}
WD = {0: 'måndag', 1: 'tysdag', 2: 'onsdag', 3: 'torsdag', 4: 'fredag',
      5: 'laurdag', 6: 'sundag'}
ORD = {1: 'fyrste', 3: 'tredje'}


def nth_weekday(y, m, wd, n):
    d = datetime(y, m, 1)
    while d.weekday() != wd:
        d += timedelta(days=1)
    return d + timedelta(weeks=n - 1)


def last_weekday(y, m, wd):
    d = datetime(y, m, calendar.monthrange(y, m)[1])
    while d.weekday() != wd:
        d -= timedelta(days=1)
    return d


def _day_span(d):
    return (AstroDate(d.year, d.month, d.day),
            AstroDate(*(d + timedelta(days=1)).timetuple()[:3]))


NTH = []
for _y in (2020, 2021):
    for _m in range(1, 13):
        for _wd in range(7):
            for _n in (1, 3):
                NTH.append((f"{ORD[_n]} {WD[_wd]} i {MONTHS[_m]} {_y}",
                            nth_weekday(_y, _m, _wd, _n)))

LAST = []
for _y in (2020, 2021):
    for _m in range(1, 13):
        for _wd in range(7):
            LAST.append((f"siste {WD[_wd]} i {MONTHS[_m]} {_y}",
                         last_weekday(_y, _m, _wd)))


@pytest.mark.parametrize("text,expected", NTH)
def test_nth_weekday_of_month(text, expected):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    s = r[0]
    assert (s.start, s.end) == _day_span(expected)
    assert s.width == timedelta(days=1)


@pytest.mark.parametrize("text,expected", LAST)
def test_last_weekday_of_month(text, expected):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    s = r[0]
    assert (s.start, s.end) == _day_span(expected)
    assert s.width == timedelta(days=1)
