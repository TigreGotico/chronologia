# -*- coding: utf-8 -*-
"""The Hungarian sublative -ra/-re after a length or a clock hour (Wiktionary, hu "perc" and "óra"). Anchor: Tuesday 2017-06-27 13:04."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

from ruling17 import next_twelve

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text,expected", [
    ("öt percre", timedelta(minutes=5)),
    ("tíz másodpercre", timedelta(seconds=10)),
    ("fél órára", timedelta(minutes=30)),
    ("egy órára", timedelta(hours=1)),
    ("két órára", timedelta(hours=2)),
    ("három napra", timedelta(days=3)),
    ("állíts be egy időzítőt öt percre", timedelta(minutes=5)),
    ("kérek egy új időzítőt fél órára", timedelta(minutes=30)),
])
def test_sublative_length(text, expected):
    got = extract_duration(text, "hu")
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text,remainder", [
    ("három órára", ""),
    ("tedd át a megbeszélést három órára", "tedd át a megbeszélést"),
])
def test_sublative_clock_hour(text, remainder):
    # said at 13:04, the next three o'clock is 15:00
    got = parse(text)
    assert got is not None, f"{text!r} did not parse"
    assert got.span.start == ad(next_twelve(ANCHOR, 3))
    assert got.remainder == remainder
