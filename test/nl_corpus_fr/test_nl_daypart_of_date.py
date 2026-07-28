# -*- coding: utf-8 -*-
"""Day-part band composed onto a named calendar date (fr):
"le matin du 3 mars", "le soir du 14 juillet", "la nuit du 3 mars".

The band offsets are the CLDR-fr day-periods already pinned in
test_nl_daypart: nuit [00:00, 04:00), matin [04:00, 12:00), soir
[18:00, 24:00).  Here they ride on an explicit date instead of a deictic day.

A date with no year takes the prefer-future year: 2017 if (month, day) is on or
after the anchor day 06-27, else 2018.  With an explicit year that year wins
outright.  ("l'après-midi du ..." is intentionally excluded: French has no bare
après-midi day-part vocabulary -- see test_nl_daypart -- so it does not compose
here and returns the whole day.)

Anchor Tuesday 2017-06-27 13:04.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end


# band -> (start-hour, end-hour, end-is-next-day)
_BAND = {
    "le matin": (4, 12, False),
    "le soir": (18, 0, True),
    "la nuit": (0, 4, False),
}


def _pf_year(month, day):
    return 2017 if (month, day) >= (6, 27) else 2018


def _expected(band, year, month, day):
    sh, eh, nextday = _BAND[band]
    s = AstroDate(year, month, day, sh, 0)
    if nextday:
        e = AstroDate(year, month, day) + __import__("datetime").timedelta(days=1)
        e = AstroDate(e.year, e.month, e.day, 0, 0)
    else:
        e = AstroDate(year, month, day, eh, 0)
    return s, e


_CASES = [
    # (text, band, month, day, year-or-None)
    ("le matin du 3 mars", "le matin", 3, 3, None),
    ("le soir du 3 mars", "le soir", 3, 3, None),
    ("la nuit du 3 mars", "la nuit", 3, 3, None),
    ("le matin du 14 juillet", "le matin", 7, 14, None),
    ("le soir du 14 juillet", "le soir", 7, 14, None),
    ("le soir du 25 décembre", "le soir", 12, 25, None),
    ("le matin du 1er janvier", "le matin", 1, 1, None),
    ("le soir du 30 juin", "le soir", 6, 30, None),
    ("le matin du 28 juin", "le matin", 6, 28, None),
    ("le matin du 15 août 2020", "le matin", 8, 15, 2020),
    ("le soir du 14 juillet 2019", "le soir", 7, 14, 2019),
    ("la nuit du 1er novembre 2021", "la nuit", 11, 1, 2021),
]


@pytest.mark.parametrize("text,band,month,day,year", _CASES)
def test_daypart_of_date(text, band, month, day, year):
    y = year if year is not None else _pf_year(month, day)
    want = _expected(band, y, month, day)
    got = start_end(text)
    assert got == want, f"{text!r} -> {got}, want {want}"
