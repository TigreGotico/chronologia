# -*- coding: utf-8 -*-
"""Ordinal-weekday-of-month (fr): "le troisième lundi de mars",
"le premier dimanche de mai", "le dernier vendredi de juin", with and without
an explicit year.

The gold is an independent enumeration: list every day of the target month
whose weekday matches, then index it (1-based) or take the last for "dernier".
The span is one day wide.  A bare month with no year binds to the anchor's own
year (2017), with no prefer-future roll -- "troisième lundi de mars" resolves
to March 2017 even though March is already past on 2017-06-27.

Several of these are the civil anchors of real French/US observances (fourth
Thursday of November = US Thanksgiving; first Monday of September = US Labor
Day), which makes the enumeration easy to cross-check by hand.

Anchor: Tuesday 2017-06-27 13:04.
"""
import calendar
from datetime import date

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import span, start_end


_WD = {"lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3,
       "vendredi": 4, "samedi": 5, "dimanche": 6}


def _nth(year, month, weekday, n):
    """Independent oracle: the n-th (or 'last') given weekday of a month."""
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if date(year, month, d).weekday() == _WD[weekday]]
    d = days[-1] if n == "last" else days[n - 1]
    return AstroDate(year, month, d)


# -- bare (anchor year 2017) -------------------------------------------------

_BARE = [
    ("le premier lundi de janvier", "lundi", 1, 1),
    ("le troisième lundi de mars", "lundi", 3, 3),
    ("le premier dimanche de mai", "dimanche", 5, 1),
    ("le dernier vendredi de juin", "vendredi", 6, "last"),
    ("le deuxième mardi de novembre", "mardi", 11, 2),
    ("le quatrième jeudi de novembre", "jeudi", 11, 4),
    ("le premier lundi de septembre", "lundi", 9, 1),
    ("le troisième dimanche de juin", "dimanche", 6, 3),
    ("le deuxième samedi d'août", "samedi", 8, 2),
    ("le dernier dimanche d'octobre", "dimanche", 10, "last"),
    ("le premier mercredi de février", "mercredi", 2, 1),
]


@pytest.mark.parametrize("text,wd,mo,n", _BARE)
def test_bare_nth_weekday(text, wd, mo, n):
    s, e = start_end(text)
    assert s == _nth(2017, mo, wd, n), f"{text!r} -> {s}"
    assert (e - s).days == 1


# -- explicit year -----------------------------------------------------------

_YEAR = [
    ("le troisième lundi de mars 2020", "lundi", 2020, 3, 3),
    ("le premier lundi de septembre 2018", "lundi", 2018, 9, 1),
    ("le quatrième jeudi de novembre 2021", "jeudi", 2021, 11, 4),
    ("le dernier dimanche de mars 2019", "dimanche", 2019, 3, "last"),
    ("le deuxième mardi d'octobre 2020", "mardi", 2020, 10, 2),
    ("le premier vendredi de mai 2025", "vendredi", 2025, 5, 1),
]


@pytest.mark.parametrize("text,wd,yr,mo,n", _YEAR)
def test_year_nth_weekday(text, wd, yr, mo, n):
    s, e = start_end(text)
    assert s == _nth(yr, mo, wd, n), f"{text!r} -> {s}"
    assert (e - s).days == 1


def test_span_is_one_day_wide():
    assert span("le troisième lundi de mars").width.days == 1


# -- comprehensive generated sweep (anchor year 2017) ------------------------
# Every month x {lundi, mercredi, vendredi, dimanche} x {1st, 2nd, last}; gold
# from the same independent enumeration. Elision "de" -> "d'" before a
# vowel-initial month name (avril, aout, octobre).

_MONTHS = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre",
    12: "décembre",
}
_ORD = {1: "premier", 2: "deuxième", 3: "troisième", 4: "quatrième"}


def _de(month):
    return "d'" if _MONTHS[month][0] in "aeiouàâäéèêëîïôöûü" else "de "


def _sweep():
    out = []
    for m in _MONTHS:
        for wd in ("lundi", "mercredi", "vendredi", "dimanche"):
            for n in (1, 2, "last"):
                word = "dernier" if n == "last" else _ORD[n]
                out.append((f"le {word} {wd} {_de(m)}{_MONTHS[m]}", wd, m, n))
    return out


@pytest.mark.parametrize("text,wd,mo,n", _sweep())
def test_sweep_nth_weekday(text, wd, mo, n):
    s, e = start_end(text)
    assert s == _nth(2017, mo, wd, n), f"{text!r} -> {s}"
    assert (e - s).days == 1
