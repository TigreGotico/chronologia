# -*- coding: utf-8 -*-
"""Romanian ordinal-weekday-of-month: "a doua luni din martie 2020".

The construction is ``<ordinal> <weekday> din <month> <year>`` and it names the
n-th occurrence of that weekday inside the given calendar month -- e.g.
"a doua luni din martie 2020" is the second Monday of March 2020. When the n-th
occurrence does not exist (a fifth Friday in a month with only four), the phrase
must not resolve to a span at all.

The gold is computed here by independent ``datetime.date`` arithmetic -- walking
to the first matching weekday of the month and stepping in weeks -- and never by
reading the parser's own output.

Ordinal surface forms that this locale accepts:
  * feminine  : a doua, a treia, a patra, a cincea, ultima
  * masculine : primul, al doilea, al treilea, al patrulea, al cincilea, ultimul
The feminine "prima" is *not* in the weekday vocabulary (see BUGS in the review
note), so "first" is spelled "primul" throughout.

Weekdays map to ``date.weekday()`` (Mon=0): luni=0, marti=1, miercuri=2,
joi=3, vineri=4, sambata=5, duminica=6.

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, timedelta
import calendar

import pytest

from ._corpus import parse, start_end, nomatch, AstroDate


_WD = {
    "luni": 0, "marți": 1, "miercuri": 2, "joi": 3,
    "vineri": 4, "sâmbătă": 5, "duminică": 6,
}

# ordinal surface -> occurrence index; "last" is a sentinel
_FEM = {"a doua": 2, "a treia": 3, "a patra": 4, "a cincea": 5}
_MASC = {"al doilea": 2, "al treilea": 3, "al patrulea": 4, "al cincilea": 5}


def _nth_weekday(y, m, wd, n):
    """Day-of-month of the n-th ``wd`` in month ``m``/``y`` or None if absent."""
    first_wd = date(y, m, 1).weekday()
    day = 1 + (wd - first_wd) % 7 + (n - 1) * 7
    return day if day <= calendar.monthrange(y, m)[1] else None


def _last_weekday(y, m, wd):
    last = calendar.monthrange(y, m)[1]
    last_wd = date(y, m, last).weekday()
    return last - (last_wd - wd) % 7


# ---------------------------------------------------------------------------
# main sweep: occurrences 1..3 (always exist) + "last", across months/years
# ---------------------------------------------------------------------------
def _main_cases():
    out = []
    for y in (2021, 2022, 2023):
        for m in range(1, 13):
            for wname, wd in _WD.items():
                out.append((f"primul {wname} din {_MONTH[m]} {y}",
                            _nth_weekday(y, m, wd, 1), y, m))
                out.append((f"a doua {wname} din {_MONTH[m]} {y}",
                            _nth_weekday(y, m, wd, 2), y, m))
                out.append((f"ultima {wname} din {_MONTH[m]} {y}",
                            _last_weekday(y, m, wd), y, m))
    return out


_MONTH = {
    1: "ianuarie", 2: "februarie", 3: "martie", 4: "aprilie", 5: "mai",
    6: "iunie", 7: "iulie", 8: "august", 9: "septembrie", 10: "octombrie",
    11: "noiembrie", 12: "decembrie",
}


@pytest.mark.parametrize("text,day,y,m", _main_cases())
def test_ordinal_weekday(text, day, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, day), text
    assert e - s == timedelta(days=1)


# ---------------------------------------------------------------------------
# masculine ordinal surfaces resolve to the same days as the feminine ones
# ---------------------------------------------------------------------------
def _masc_cases():
    out = []
    for y in (2024,):
        for m in (3, 6, 9, 12):
            for wname, wd in _WD.items():
                for surf, n in (("al doilea", 2), ("al treilea", 3)):
                    out.append((f"{surf} {wname} din {_MONTH[m]} {y}",
                                _nth_weekday(y, m, wd, n), y, m))
                out.append((f"ultimul {wname} din {_MONTH[m]} {y}",
                            _last_weekday(y, m, wd), y, m))
    return out


@pytest.mark.parametrize("text,day,y,m", _masc_cases())
def test_ordinal_weekday_masculine(text, day, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, day), text
    assert e - s == timedelta(days=1)


# ---------------------------------------------------------------------------
# the fifth occurrence: present in some months, absent in others.
# Present -> exact day; absent -> the phrase must not resolve.
# ---------------------------------------------------------------------------
def _fifth_cases():
    out = []
    for y in (2020, 2021):
        for m in range(1, 13):
            for wname, wd in _WD.items():
                day = _nth_weekday(y, m, wd, 5)
                out.append((f"a cincea {wname} din {_MONTH[m]} {y}", day, y, m))
    return out


@pytest.mark.parametrize("text,day,y,m", _fifth_cases())
def test_fifth_weekday(text, day, y, m):
    if day is None:
        nomatch(text)
    else:
        s, e = start_end(text)
        assert s == AstroDate(y, m, day), text
        assert e - s == timedelta(days=1)
