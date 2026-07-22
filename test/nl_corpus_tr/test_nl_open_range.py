# -*- coding: utf-8 -*-
"""Open-ended ranges (tr): Turkish frames the closed end with the **postposed**
"kadar" ("<date>('e) kadar" = until <date>), so the engine's postposed
open-range scan expresses it natively (open start bounded below by "now").

Homograph note: "kadar" also means "as much as / about"; the engine only reads
it as the range marker when the head parses as a date endpoint. The dative
suffix Turkish adds to the date noun ("cumaya kadar") is a downstream
morphology concern -- the bare/uninflected head is what the engine reads."""
from datetime import datetime
from chronologia.extract import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2017, 6, 27, 13, 4)
NOW = AstroDate.from_datetime(A)


def _span(text):
    r = extract_timespan(text, "tr", anchor=A)
    assert r is not None, f"{text!r} did not parse"
    return r[0]


def test_kadar_open_start_year():
    s = _span("2020 kadar")
    assert s.start == NOW and s.end == AstroDate(2021, 1, 1)


def test_kadar_open_start_weekday():
    s = _span("cuma kadar")
    assert s.start == NOW and s.end == AstroDate(2017, 7, 1)


def test_bare_kadar_is_not_a_range():
    assert extract_timespan("kadar", "tr", anchor=A) is None
