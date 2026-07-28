# -*- coding: utf-8 -*-
"""Polish month-third fuzzy spans (początek / połowa / koniec MONTH), swept
across all twelve months (marca is already covered in test_nl_month_fuzzy.py
and is skipped here).

Order shape: Slavic genitive, no connector -- PART MONTH(gen).  Each third is
the first / middle / last arithmetic third of the parent calendar month, sliced
by :func:`chronologia.subdivide`.  The parent month edges and the third
boundaries are computed here with pure ``datetime`` arithmetic; the parser is
never used to produce the expected values.  Bare month with no year resolves in
the anchor year 2017.

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


def _cases():
    out = []
    for mi, mon in enumerate(_MON, 1):
        if mon == "marca":
            continue  # covered in test_nl_month_fuzzy.py
        for word, part in _PART:
            gs, ge = _third(_YEAR, mi, part)
            out.append((f"{word} {mon}", gs, ge))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,gs,ge", _CASES, ids=[c[0] for c in _CASES])
def test_month_third(text, gs, ge):
    assert start_end(text) == (gs, ge)
