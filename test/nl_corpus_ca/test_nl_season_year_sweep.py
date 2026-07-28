# -*- coding: utf-8 -*-
"""Season + explicit-year sweep for Catalan.

Meteorological seasons (northern hemisphere, 3-month blocks) bind the stated
year (verified independently of the parser).  Winter starts in December of the
named year and runs into March of the next.  Expected bounds are pure
arithmetic here.  Article-carrying phrasings ("la primavera de", "l'hivern de")
keep every (phrase) distinct from the article-less cases already in
``test_nl_scoped_seasons``.
"""
from datetime import datetime

import pytest

from ._corpus import start_end, AstroDate

# name -> (article-phrase, start-month, span-in-months)
_SEASONS = [
    ("la primavera de", 3, 3),
    ("l'estiu de", 6, 3),
    ("la tardor de", 9, 3),
    ("l'hivern de", 12, 3),
]

_YEARS = range(1981, 2021)  # 40 years


def _cases():
    out = []
    for phrase, sm, _ in _SEASONS:
        for y in _YEARS:
            text = "%s %d" % (phrase, y)
            s = datetime(y, sm, 1)
            end_year, end_month = (y, sm + 3)
            if end_month > 12:
                end_year, end_month = y + 1, end_month - 12
            e = datetime(end_year, end_month, 1)
            out.append((text, s, e))
    return out


_CASES = _cases()


@pytest.mark.parametrize(
    "text,s,e", _CASES, ids=[t for t, _, _ in _CASES]
)
def test_season_of_year(text, s, e):
    gs, ge = start_end(text)
    assert gs == AstroDate(s.year, s.month, s.day)
    assert ge == AstroDate(e.year, e.month, e.day)
