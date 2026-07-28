# -*- coding: utf-8 -*-
""""início / meados / fim de <mês>": the three equal calendar thirds of a
named month.

A named month is split into three equal parts by wall-clock time, not by whole
days, so the boundaries fall on a fraction of a day whenever the month's length
is not a multiple of three.  For a month of N days starting at midnight of the
first, the cut points are

    day 1 00:00  +  k * (N / 3) days     for k = 0, 1, 2, 3

so June (N=30) splits cleanly into 10-day thirds, while March (N=31) puts the
first cut at the 11th 08:00 (31/3 = 10 d 8 h) and February 2017 (N=28) at the
10th 08:00 (28/3 = 9 d 8 h).  The oracle below is this arithmetic run against
``calendar.monthrange`` -- the parser is never consulted for the gold.

"início" and "princípios" name the first third, "meados" the middle, "fim" /
"fins" / "final" the last.  [[EP vs BP]]: shared vocabulary; both norms say
"meados de março" and "fins de agosto".  Anchor 2017-06-27 is irrelevant here
-- a named month with no year resolves within the anchor's own year.
"""
from calendar import monthrange
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, start_end, parse

_MONTHS = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio",
           6: "junho", 7: "julho", 8: "agosto", 9: "setembro", 10: "outubro",
           11: "novembro", 12: "dezembro"}

#: lead word -> which third (1, 2 or 3) it names
_LEADS = {"início": 1, "princípios": 1, "meados": 2,
          "fim": 3, "fins": 3, "final": 3}

_YEAR = 2017


def _third_edges(month, third):
    n = monthrange(_YEAR, month)[1]
    base = datetime(_YEAR, month, 1)
    cuts = [base + timedelta(days=n) * k / 3 for k in range(4)]
    return cuts[third - 1], cuts[third]


def _cases():
    out = []
    for lead, third in _LEADS.items():
        for m in _MONTHS:
            out.append((f"{lead} de {_MONTHS[m]}", m, third))
    return out


@pytest.mark.parametrize("text,month,third", _cases())
def test_month_third(text, month, third):
    gs, ge = _third_edges(month, third)
    s, e = start_end(text)
    assert s == AstroDate.from_datetime(gs), f"{text!r} start {s}"
    assert e == AstroDate.from_datetime(ge), f"{text!r} end {e}"


def test_thirds_tile_the_whole_month():
    """The three thirds of a month meet edge-to-edge and cover it exactly."""
    _, e1 = start_end("início de março")
    s2, e2 = start_end("meados de março")
    s3, _ = start_end("fim de março")
    assert e1 == s2 and e2 == s3
    assert start_end("início de março")[0] == AstroDate(2017, 3, 1)
    assert start_end("fim de março")[1] == AstroDate(2017, 4, 1)


@pytest.mark.parametrize("text", ["início de", "meados de xpto", "fim de mês"])
def test_garbage_never_raises(text):
    parse(text)
