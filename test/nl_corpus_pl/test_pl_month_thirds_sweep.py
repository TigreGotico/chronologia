# -*- coding: utf-8 -*-
"""Polish month-third fuzzy spans (początek / połowa / koniec MONTH), swept
across all twelve months (marca is already covered in test_nl_month_fuzzy.py
and is skipped here).

Order shape: Slavic genitive, no connector -- PART MONTH(gen).  Each third is
the first / middle / last arithmetic third of the parent calendar month, sliced
by :func:`chronologia.subdivide`.  The parent month edges and the third
boundaries are computed here with pure ``datetime`` arithmetic; the parser is
never used to produce the expected values.  A bare month with no year takes the
year the month alone takes (ruling 1, changed 26 November 2026): 2018 for
January to May, 2017 for June to December.

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from ._corpus import AstroDate, start_end

_MON = [
    "stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca",
    "lipca", "sierpnia", "września", "października", "listopada", "grudnia",
]
_PART = [("początek", "early"), ("połowa", "mid"), ("koniec", "late")]

_YEAR = 2017


def _third(year, month, part):
    s = datetime(year, month, 1)
    e = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    w = (e - s) / 3
    lo, hi = {"early": (s, s + w), "mid": (s + w, s + 2 * w),
              "late": (s + 2 * w, e)}[part]
    return AstroDate.from_datetime(lo), AstroDate.from_datetime(hi)


_ANCHOR = datetime(2017, 6, 27, 13, 4)


def _third_end_dt(year, month, part):
    s = datetime(year, month, 1)
    e = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    w = (e - s) / 3
    return {"early": s + w, "mid": s + 2 * w, "late": e}[part]


def _cases():
    out = []
    for mi, mon in enumerate(_MON, 1):
        if mon == "marca":
            continue  # covered in test_nl_month_fuzzy.py
        for word, part in _PART:
            # ruling 1 (changed 26 November 2026): a part of a month takes its month's year; a month that has ended at the anchor is next year's
            gs, ge = _third(_YEAR + (mi < 6), mi, part)
            # ruling 1 (26 November 2026): a part of a month is read as a
            # span; a part of the anchor's own month that has ended at
            # 2017-06-27 13:04 (początek, połowa of June) is June 2018, the
            # part that holds it (koniec) stays 2017
            if mi == 6 and _third_end_dt(_YEAR, mi, part) <= _ANCHOR:
                gs, ge = _third(_YEAR + 1, mi, part)
            out.append((f"{word} {mon}", gs, ge))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,gs,ge", _CASES, ids=[c[0] for c in _CASES])
def test_month_third(text, gs, ge):
    assert start_end(text) == (gs, ge)
