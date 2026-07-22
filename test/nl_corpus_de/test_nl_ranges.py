# -*- coding: utf-8 -*-
"""German ranges: "von A bis B" / "zwischen A und B" plus dash framings, and
the open-ended "bis" (open start) / "seit" (open end) forms.

Endpoints are two independent sub-parses; the span runs from the start of the
left to the end of the right.  The prefer-future frame stays consistent across
both endpoints even when the range straddles "now" (anchor 2017-06-27).
"""
import pytest

from ._corpus import AstroDate, start_end, nomatch, ANCHOR, ad


def _d(s):
    return AstroDate(*(int(x) for x in s.split("-")))


@pytest.mark.parametrize("text,s,e", [
    ("20. juni - 30. juni", "2017-6-20", "2017-7-1"),        # straddle, dash
    ("von 20. juni bis 30. juni", "2017-6-20", "2017-7-1"),  # straddle, word
    ("1. juni - 10. juni", "2018-6-1", "2018-6-11"),         # both behind
    ("25. juni - 5. juli", "2017-6-25", "2017-7-6"),         # cross-month
    ("10. august - 20. september", "2017-8-10", "2017-9-21"),
    ("28. dezember - 3. januar", "2017-12-28", "2018-1-4"),  # cross-year
    ("3. märz 2001 - 9. märz 2001", "2001-3-3", "2001-3-10"),  # explicit years
    ("zwischen juli und september", "2017-7-1", "2017-10-1"),  # month, word
    ("juni - august", "2017-6-1", "2017-9-1"),               # month, dash
])
def test_date_and_month_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


# -- open-ended ranges: "bis" (open start) / "seit" (open end) --------------

def test_bis_open_start():
    s, e = start_end("bis freitag")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)


def test_seit_open_end():
    s, e = start_end("seit 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)


@pytest.mark.parametrize("text", ["von apfel bis birne", "von hier bis dort"])
def test_non_temporal_range_is_none(text):
    nomatch(text)
