# -*- coding: utf-8 -*-
"""Open-ended ranges (fi): Finnish frames the closed end with a **postposed**
marker -- "<date> asti" / "<date> saakka" (until <date>) -- so the engine's
postposed open-range scan expresses it natively (open start bounded below by
"now"). Endpoints hand-derived against the mission anchor."""
from datetime import datetime
from chronologia.extract import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2017, 6, 27, 13, 4)
NOW = AstroDate.from_datetime(A)


def _span(text):
    r = extract_timespan(text, "fi", anchor=A)
    assert r is not None, f"{text!r} did not parse"
    return r[0]


def test_asti_open_start_year():
    s = _span("2020 asti")
    assert s.start == NOW and s.end == AstroDate(2021, 1, 1)


def test_saakka_open_start_year():
    s = _span("2020 saakka")
    assert s.start == NOW and s.end == AstroDate(2021, 1, 1)


def test_asti_open_start_weekday():
    s = _span("perjantai asti")
    assert s.start == NOW and s.end == AstroDate(2017, 7, 1)


def test_bare_marker_not_a_range():
    # a lone marker with no date endpoint is not an open range
    assert extract_timespan("asti", "fi", anchor=A) is None
