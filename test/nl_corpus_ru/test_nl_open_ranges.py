# -*- coding: utf-8 -*-
"""Open-ended ranges (ru): a leading ``until``/``since`` marker with a parseable
date endpoint. ``until`` opens the start (pinned to now) and keeps the
endpoint's ``.end``; ``since`` opens the end (pinned to now) and keeps the
endpoint's ``.start``. Anchor 2017-06-27 13:04. Every edge hand-derived."""
import pytest
from ._corpus import ANCHOR, AstroDate, ad, start_end, nomatch


@pytest.mark.parametrize("text,e", [
    ("до 2020", (2021, 1, 1)),
    ("до 2019", (2020, 1, 1)),
    ("до декабря", (2018, 1, 1)),
])
def test_until_open_start(text, e):
    s, ee = start_end(text)
    assert s == ad(ANCHOR)
    assert ee == AstroDate(*e)


@pytest.mark.parametrize("text,s", [
    ("с 2010", (2010, 1, 1)),
    ("с 2000", (2000, 1, 1)),
    ("с 2015", (2015, 1, 1)),
])
def test_since_open_end(text, s):
    ss, e = start_end(text)
    assert ss == AstroDate(*s)
    assert e == ad(ANCHOR)


@pytest.mark.parametrize("text", ["до", "встречу"])
def test_no_open_range(text):
    nomatch(text)
