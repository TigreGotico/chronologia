# -*- coding: utf-8 -*-
"""German ordinal-weekday-of-month: "der dritte Montag im März 2020".

The idiom names the Nth occurrence of a weekday inside a month. The oracle is
independent arithmetic (:func:`_nth_weekday` walks the month counting matching
weekdays); the parser is never consulted for the gold. Cardinal ordinals
erste..fünfte are exercised across 2018-2021 and several months, each landing
a day-wide span.

The "letzter <weekday> im <Monat>" (last-of-month) form is NOT supported: it
strands its scope and falls back to the plain weekday-relative reading. That
gap is recorded in :func:`test_last_weekday_of_month_is_unsupported` so the
approval verdict can cite it.

Anchor 2017-06-27 (Dienstag).
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, parse

_WD = {"montag": 0, "dienstag": 1, "mittwoch": 2, "donnerstag": 3,
       "freitag": 4, "samstag": 5, "sonntag": 6}
_ORD = {1: "erste", 2: "zweite", 3: "dritte", 4: "vierte", 5: "fünfte"}
_MO = ["", "januar", "februar", "märz", "april", "mai", "juni", "juli",
       "august", "september", "oktober", "november", "dezember"]


def _nth_weekday(y, m, wd, n):
    c = 0
    for d in range(1, calendar.monthrange(y, m)[1] + 1):
        if date(y, m, d).weekday() == wd:
            c += 1
            if c == n:
                return date(y, m, d)
    return None


_RAW = [
    (2018, 3, "montag", 2), (2019, 5, "sonntag", 2), (2020, 1, "freitag", 1),
    (2020, 11, "donnerstag", 3), (2020, 6, "montag", 5), (2021, 4, "dienstag", 3),
    (2019, 10, "mittwoch", 4), (2018, 12, "samstag", 1), (2020, 2, "samstag", 4),
    (2021, 7, "freitag", 2), (2019, 9, "montag", 1), (2020, 8, "sonntag", 5),
    (2019, 3, "montag", 3), (2020, 3, "montag", 3), (2017, 11, "donnerstag", 4),
]

_CASES = []
for _y, _m, _wd, _n in _RAW:
    _d = _nth_weekday(_y, _m, _WD[_wd], _n)
    assert _d is not None, (_y, _m, _wd, _n)  # oracle sanity, not the parser
    _CASES.append((f"der {_ORD[_n]} {_wd} im {_MO[_m]} {_y}", _d))


@pytest.mark.parametrize("text,d", _CASES)
def test_ordinal_weekday_of_month(text, d):
    sp = span(text)
    assert sp.start == AstroDate(d.year, d.month, d.day), f"{text!r} -> {sp}"
    assert sp.end == AstroDate(*(d + timedelta(days=1)).timetuple()[:3])


def test_last_weekday_of_month_is_unsupported():
    """"der letzte Montag im Mai" is not read as last-of-month.

    Gold (independent): the last Monday of May 2017 is the 29th. The engine
    instead binds the plain "letzten Montag" (previous Monday from the anchor,
    26 June) and strands "der im mai". Documented, not silently accepted.
    """
    r = parse("der letzte montag im mai")
    assert r is not None
    # NOT the correct last-of-month answer -- feature gap, tracked in approval
    assert r[0].start != AstroDate(2017, 5, 29)
