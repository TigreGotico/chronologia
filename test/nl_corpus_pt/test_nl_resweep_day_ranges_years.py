# -*- coding: utf-8 -*-
"""Second-pass sweep: "de N a M de <mês> de <ano>" day-ranges (shared-month,
explicit year) across all twelve months and five fresh years (2013, 2019,
2023, 2027, 2032) -- none overlapping the small hand-picked sample already
pinned in test_nl_ranges.py (which only names an explicit year once, 2001).

Gold is independent: the end of a day range is the day AFTER the closing day
(half-open span), computed with plain ``timedelta`` arithmetic, never read
back from the parser. Every pair here (5, 20) stays inside its own month so
no case straddles a month/year boundary -- that boundary-crossing behaviour
is already pinned in test_nl_ranges.py.

Anchor Tuesday 2017-06-27 13:04, irrelevant since every case names its own
year.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

_MONTHS = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio",
           6: "junho", 7: "julho", 8: "agosto", 9: "setembro",
           10: "outubro", 11: "novembro", 12: "dezembro"}

_YEARS = [2013, 2019, 2023, 2027, 2032]


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


def _sweep():
    out = []
    for y in _YEARS:
        for m in _MONTHS:
            text = f"de 5 a 20 de {_MONTHS[m]} de {y}"
            start = date(y, m, 5)
            end = date(y, m, 20) + timedelta(days=1)
            out.append((text, y, m, start, end))
    return out


@pytest.mark.parametrize("text,y,m,gs,ge", _sweep())
def test_shared_month_day_range_explicit_year(text, y, m, gs, ge):
    s, e = start_end(text)
    assert s == _ad(gs), f"{text!r} -> start {s}"
    assert e == _ad(ge), f"{text!r} -> end {e}"
