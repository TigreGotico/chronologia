# -*- coding: utf-8 -*-
"""Second-pass sweep: ordinal-weekday-of-month with an EXPLICIT year, across
all seven weekdays, all twelve months, {primeiro, segundo, terceiro, quarto,
último} and four years spread across three decades (2015, 2021, 2024, 2030)
-- none overlapping the small hand-picked anchor-year (2017) sample already
pinned in test_nl_ordinal_weekday.py (which also deliberately skips "segunda"
and "quarta" as ORDINAL words to dodge their weekday-noun homograph).  Here
the masculine article "o" is used uniformly with every ordinal/weekday pair
-- independently verified against the parser that "o segundo segunda-feira"
and "o quarto quarta-feira" both resolve correctly despite the surface
gender mismatch, so the homograph trap that motivated the exclusion in the
anchor-year file does not reappear under the masculine article.

The gold is the same independent enumeration used there: list every day of
the target month whose weekday matches, then index it (1-based) or take the
last for "último". The span is one day wide.

Anchor Tuesday 2017-06-27 13:04 (irrelevant here since every case names its
own year).
"""
from calendar import monthrange
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

_WD = {"segunda-feira": 0, "terça-feira": 1, "quarta-feira": 2,
       "quinta-feira": 3, "sexta-feira": 4, "sábado": 5, "domingo": 6}

_MONTHS = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio",
           6: "junho", 7: "julho", 8: "agosto", 9: "setembro",
           10: "outubro", 11: "novembro", 12: "dezembro"}

_ORD = {1: "primeiro", 2: "segundo", 3: "terceiro", 4: "quarto"}

_YEARS = [2015, 2021, 2024, 2030]


def _nth(year, month, weekday, n):
    days = [d for d in range(1, monthrange(year, month)[1] + 1)
            if datetime(year, month, d).weekday() == weekday]
    d = days[-1] if n == "last" else days[n - 1]
    return AstroDate(year, month, d)


def _sweep():
    out = []
    for y in _YEARS:
        for m in _MONTHS:
            for wname, wd in _WD.items():
                for n in (1, 2, 3, 4, "last"):
                    word = "último" if n == "last" else _ORD[n]
                    text = f"o {word} {wname} de {_MONTHS[m]} de {y}"
                    out.append((text, y, wd, m, n))
    return out


@pytest.mark.parametrize("text,y,wd,mo,n", _sweep())
def test_explicit_year_nth_weekday_sweep(text, y, wd, mo, n):
    s, e = start_end(text)
    assert s == _nth(y, mo, wd, n), f"{text!r} -> {s}"
    assert (e - s).days == 1
