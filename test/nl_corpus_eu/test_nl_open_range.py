# -*- coding: utf-8 -*-
"""Open-ended ranges (eu): Basque frames the closed end with the **postposed**
"arte" ("<date> arte" = until <date>), so the engine's postposed open-range
scan expresses it natively (open start bounded below by "now").

Homograph note: "arte" is genuinely ambiguous in Basque -- it means both
"until" and "art". The engine only reads it as the range marker when the head
parses as a date endpoint; a lone "arte" (or a phrase whose head is not a date)
never yields a range. This is a documented, accepted limitation."""
from datetime import datetime
from chronologia.extract import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2017, 6, 27, 13, 4)
NOW = AstroDate.from_datetime(A)


def _span(text):
    r = extract_timespan(text, "eu", anchor=A)
    assert r is not None, f"{text!r} did not parse"
    return r[0]


def test_arte_open_start_year():
    s = _span("2020 arte")
    assert s.start == NOW and s.end == AstroDate(2021, 1, 1)


def test_arte_open_start_weekday():
    s = _span("ostirala arte")
    assert s.start == NOW and s.end == AstroDate(2017, 7, 1)


def test_bare_arte_is_not_a_range():
    # the "art" homograph: "arte" alone carries no date endpoint
    assert extract_timespan("arte", "eu", anchor=A) is None
