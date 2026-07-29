# -*- coding: utf-8 -*-
"""Second-pass sweep: ordinal-weekday-of-month with an EXPLICIT year, across
all seven weekdays, all twelve months, {premier, deuxième, troisième,
dernier}, and five years spread across two decades (2015, 2019, 2022, 2024,
2028) -- none overlapping the small hand-picked sample already pinned in
test_nl_nth_weekday_of_month.py.

The gold is the same independent enumeration used there: list every day of
the target month whose weekday matches, then index it (1-based) or take the
last for "dernier". The span is one day wide.

Anchor: Tuesday 2017-06-27 13:04 (irrelevant here since every case names its
own year).
"""
import calendar
from datetime import date

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end


_WD = {"lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3,
       "vendredi": 4, "samedi": 5, "dimanche": 6}

_MONTHS = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre",
    12: "décembre",
}
_ORD = {1: "premier", 2: "deuxième", 3: "troisième"}

_YEARS = [2015, 2019, 2022, 2024, 2028]


def _de(month):
    return "d'" if _MONTHS[month][0] in "aeiouàâäéèêëîïôöûü" else "de "


def _nth(year, month, weekday, n):
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if date(year, month, d).weekday() == _WD[weekday]]
    d = days[-1] if n == "last" else days[n - 1]
    return AstroDate(year, month, d)


def _sweep():
    out = []
    for y in _YEARS:
        for m in _MONTHS:
            for wd in _WD:
                for n in (1, 2, 3, "last"):
                    word = "dernier" if n == "last" else _ORD[n]
                    out.append(
                        (f"le {word} {wd} {_de(m)}{_MONTHS[m]} {y}", y, wd, m, n))
    return out


@pytest.mark.parametrize("text,y,wd,mo,n", _sweep())
def test_explicit_year_nth_weekday_sweep(text, y, wd, mo, n):
    s, e = start_end(text)
    assert s == _nth(y, mo, wd, n), f"{text!r} -> {s}"
    assert (e - s).days == 1
