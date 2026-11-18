# -*- coding: utf-8 -*-
"""Open-ended ranges (bg): a leading ``until``/``since`` marker with a parseable
date endpoint. ``until`` opens the start (pinned to now) and keeps the
endpoint's ``.end``; ``since`` opens the end (pinned to now) and keeps the
endpoint's ``.start``. Anchor 2017-06-27 13:04. Every edge hand-derived."""
import pytest
from ._corpus import ANCHOR, AstroDate, ad, span, start, start_end, nomatch


@pytest.mark.parametrize("text,e", [
    ("до 2020", (2021, 1, 1)),
    ("до 2019", (2020, 1, 1)),
    ("до декември", (2018, 1, 1)),
])
def test_until_open_start(text, e):
    s, ee = start_end(text)
    assert s == ad(ANCHOR)
    assert ee == AstroDate(*e)


@pytest.mark.parametrize("text,s", [
    ("от 2010", (2010, 1, 1)),
    ("от 2000", (2000, 1, 1)),
    ("от 2015", (2015, 1, 1)),
])
def test_since_open_end(text, s):
    ss, e = start_end(text)
    assert ss == AstroDate(*s)
    assert e == ad(ANCHOR)


@pytest.mark.parametrize("text", ["до", "срещата"])
def test_no_open_range(text):
    nomatch(text)


@pytest.mark.parametrize("text, start", [
    # the next January after 27 June 2017 is January 2018
    ("след 2030", AstroDate(2031, 1, 1)),
    ("след януари", AstroDate(2018, 2, 1)),
])
def test_after_is_open_not_the_bare_x(text, start):
    # "after X" is the open span from the end of X, never the bare X reading
    s = span(text)
    assert (s.start, s.open_end) == (start, True)


@pytest.mark.parametrize("text,e", [
    ("след 3 дни", (2017, 6, 30, 13, 4)),
    ("след 5 работни дни", (2017, 7, 4)),
])
def test_after_marker_offset_reading_unaffected(text, e):
    # "след" is also the "in N units" offset marker ("след 3 дни" = "in 3
    # days") -- a distinct construction from the after-year open range above
    # and must keep resolving.
    s = start(text)
    assert s == AstroDate(*e)
