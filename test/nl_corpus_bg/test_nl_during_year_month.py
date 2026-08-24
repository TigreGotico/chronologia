# -*- coding: utf-8 -*-
""""during/in" + year and "during/in" + month (bg): "през"/"в" open a
calendar_date or year_ref span exactly like the bare form, consuming the
marker instead of stranding it as a remainder. "след" stays a distinct
surface: it is the future-offset marker ("след 5 дни" = "in 5 days") and
must keep refusing an open-ended "after <year/month>" reading. Anchor
2017-06-27 13:04. Every edge hand-derived."""
import pytest

from ._corpus import ANCHOR, AstroDate, ad, parse, span, start, nomatch


@pytest.mark.parametrize("text,y", [
    ("през 2030", 2030),
    ("в 2030", 2030),
    ("2030", 2030),
])
def test_during_year_consumes_marker(text, y):
    r = parse(text)
    assert r.span.start == AstroDate(y, 1, 1)
    assert r.span.end == AstroDate(y + 1, 1, 1)
    assert r.remainder == ""


@pytest.mark.parametrize("text,m", [
    ("през януари", 1),
    ("в януари", 1),
    ("януари", 1),
])
def test_during_month_consumes_marker(text, m):
    r = parse(text)
    assert r.span.start == AstroDate(ANCHOR.year, m, 1)
    assert r.span.end == AstroDate(ANCHOR.year, m + 1, 1)
    assert r.remainder == ""


@pytest.mark.parametrize("text", ["след 2030", "след януари"])
def test_after_still_refuses(text):
    # "след" is not a during/in surface -- an open-ended "after <year>" span
    # has no DateSpan representation and must still be refused.
    nomatch(text)


@pytest.mark.parametrize("text,e", [
    ("след 3 дни", (2017, 6, 30, 13, 4)),
    ("след 5 работни дни", (2017, 7, 4)),
])
def test_after_offset_reading_unaffected(text, e):
    # "след" keeps resolving the distinct "in N units" offset construction.
    s = start(text)
    assert s == AstroDate(*e)
