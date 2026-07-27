"""Period-end / period-start / last-day narrowing across scopes.

A verified silent-wrong cluster: the "end of" / "beginning of" narrowing
modifier (and the "last day of" civil-day selector) worked for a MONTH scope
but was STRANDED for QUARTER and FISCAL-YEAR / YEAR scopes -- the whole period
resolved and the modifier fell into the remainder, or (for "last day of the
quarter") "last day" was mis-read as "last=previous day" == yesterday.

The reference is the MONTH scope, which already narrows correctly; it is pinned
here as a regression anchor.  Expected narrow spans are derived independently
via :func:`chronologia.subdivide` over a whole-period span built by hand (the
same span-native thirds the month scope uses), never by pinning engine output.
Last-day spans are pure civil-day arithmetic.
"""
from datetime import timedelta

import pytest

from chronologia import subdivide
from chronologia.astrodate import AstroDate, DateSpan

from ._corpus import ANCHOR, parse, span, start_end


def _whole(y1, m1, d1, y2, m2, d2):
    return DateSpan(AstroDate(y1, m1, d1), AstroDate(y2, m2, d2))


# whole-period spans for the anchor (Tue 2017-06-27); Q2 = Apr-Jun, Q3 = Jul-Sep
JUNE = _whole(2017, 6, 1, 2017, 7, 1)
Q2 = _whole(2017, 4, 1, 2017, 7, 1)
Q3 = _whole(2017, 7, 1, 2017, 10, 1)
FY2019 = _whole(2019, 1, 1, 2020, 1, 1)


def _narrow(text, whole, part):
    s = span(text)
    want = subdivide(whole, part)
    assert (s.start, s.end) == (want.start, want.end), \
        f"{text!r} -> {(s.start, s.end)}, want {(want.start, want.end)}"


# -- REFERENCE: month scope already narrows (regression pin) --------------
def test_end_of_month_reference():
    _narrow("end of the month", JUNE, "late")
    _narrow("end of month", JUNE, "late")


# -- "end of" narrows the QUARTER scope -----------------------------------
@pytest.mark.parametrize("text, whole", [
    ("end of Q3", Q3),
    ("end of Q2", Q2),
    ("end of the quarter", Q2),           # anchor's own quarter
])
def test_end_of_quarter_narrows(text, whole):
    _narrow(text, whole, "late")


def test_start_of_quarter_narrows():
    _narrow("start of Q3", Q3, "early")


# -- "end of" narrows the FISCAL-YEAR / YEAR scope ------------------------
# fiscal year == calendar year in this library; the narrowing is the year's
# last third, mirroring end-of-month.
@pytest.mark.parametrize("text", [
    "end of fiscal year 2019",
    "the 2019 fiscal year end",
    "end of year 2019",
])
def test_end_of_fiscal_year_narrows(text):
    _narrow(text, FY2019, "late")


# -- "last day of <period>" -> the single final civil day -----------------
@pytest.mark.parametrize("text, y, m, d", [
    ("last day of the month", 2017, 6, 30),
    ("last day of the quarter", 2017, 6, 30),   # was 'yesterday' (2017-06-26)
    ("last day of Q3", 2017, 9, 30),
])
def test_last_day_of_period(text, y, m, d):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(y, m, d),
                      AstroDate(y, m, d) + timedelta(days=1)), \
        f"{text!r} -> {(s, e)}"
