# -*- coding: utf-8 -*-
"""Romanian month-thirds over named months: "inceputul/mijlocul/sfarsitul lui
<month> <year>".

Each phrase names the first / middle / last arithmetic third of that calendar
month. The parent month edges are ``[(y, m, 1), (y, m+1, 1))`` and the expected
third is pure ``timedelta`` arithmetic on those edges -- the same construction
the generic ``test_nl_fuzzy_period`` uses for "luna"/"an", extended here to the
twelve named months so a month that silently took the wrong width would be
caught.

Only the "lui <month>" surface carries the fuzzy sub-span; "inceputul lunii
<month>" is a different (un-thirded) reading and is deliberately not asserted
here. Gold is computed independently of the parser.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, AstroDate


_MONTH = {
    1: "ianuarie", 2: "februarie", 3: "martie", 4: "aprilie", 5: "mai",
    6: "iunie", 7: "iulie", 8: "august", 9: "septembrie", 10: "octombrie",
    11: "noiembrie", 12: "decembrie",
}
_PART = {"început": "early", "mijloc": "mid", "sfârșit": "late"}


def _third(y, m, part):
    s = datetime(y, m, 1)
    e = datetime(y + (m == 12), m % 12 + 1, 1)
    w = (e - s) / 3
    lo, hi = {"early": (s, s + w),
              "mid": (s + w, s + 2 * w),
              "late": (s + 2 * w, e)}[part]
    return AstroDate.from_datetime(lo), AstroDate.from_datetime(hi)


def _cases():
    out = []
    for y in (2019, 2020, 2021, 2022):
        for m in range(1, 13):
            for word, part in _PART.items():
                out.append((f"{word}ul lui {_MONTH[m]} {y}", y, m, part))
    return out


@pytest.mark.parametrize("text,y,m,part", _cases())
def test_month_third(text, y, m, part):
    want_s, want_e = _third(y, m, part)
    s, e = start_end(text)
    assert s == want_s, text
    assert e == want_e, text
