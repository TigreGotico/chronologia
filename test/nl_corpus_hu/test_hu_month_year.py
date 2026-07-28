"""Hungarian month + year references ("2014. szeptember") that bind a whole
calendar month.  The year leads with the ordinal dot, then the month name; the
span runs from the first of that month to the first of the next.  The end is
computed by independent arithmetic (month + 1, with a December wrap), never
from the parser.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end

MONTHS = [
    "január", "február", "március", "április", "május", "június",
    "július", "augusztus", "szeptember", "október", "november", "december",
]

_CASES = [(y, mo) for y in range(2010, 2026) for mo in range(1, 13)]


@pytest.mark.parametrize("y,mo", _CASES)
def test_month_year_span(y, mo):
    text = f"{y}. {MONTHS[mo - 1]}"
    s = datetime(y, mo, 1)
    e = datetime(y + 1, 1, 1) if mo == 12 else datetime(y, mo + 1, 1)
    assert start_end(text) == (ad(s), ad(e))
