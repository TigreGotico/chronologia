# -*- coding: utf-8 -*-
"""sv: bare intra-month day ranges swept across months.

Forms: "D1-D2 <month>", "den D1-D2 <month>", "från D1 till D2 <month>".
The span is [D1, D2] inclusive, so the exclusive end is D2+1. Bare (no year)
means prefer-future decides the year: the start day resolves in 2017 if it is
on/after the anchor, otherwise it rolls to 2018. That roll is replicated here
by INDEPENDENT arithmetic against the shared ANCHOR, never read from the parser.

Anchor Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, start_end

_MONTHS = {
    1: "januari", 2: "februari", 3: "mars", 4: "april", 5: "maj", 6: "juni",
    7: "juli", 8: "augusti", 9: "september", 10: "oktober", 11: "november",
    12: "december",
}
# pairs kept strictly inside a month and never straddling the anchor day (27),
# so the prefer-future year is unambiguous from either endpoint.
_PAIRS = [(5, 12), (3, 8), (1, 15), (10, 20), (14, 22)]
_FORMS = [
    lambda d1, d2, m: f"{d1}-{d2} {m}",
    lambda d1, d2, m: f"den {d1}-{d2} {m}",
    lambda d1, d2, m: f"från {d1} till {d2} {m}",
]


def _year_for(mo, d1):
    cand = datetime(2017, mo, d1)
    return 2017 if cand >= ANCHOR else 2018


def _build():
    cases = []
    for mo in range(1, 13):
        for d1, d2 in _PAIRS:
            yr = _year_for(mo, d1)
            gs = AstroDate(yr, mo, d1)
            e = datetime(yr, mo, d2) + timedelta(days=1)
            ge = AstroDate(e.year, e.month, e.day)
            for form in _FORMS:
                cases.append((form(d1, d2, _MONTHS[mo]), gs, ge))
    return cases


_CASES = _build()


@pytest.mark.parametrize("text,gs,ge", _CASES, ids=[c[0] for c in _CASES])
def test_day_range(text, gs, ge):
    assert start_end(text) == (gs, ge)
