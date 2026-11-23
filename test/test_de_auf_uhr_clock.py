# -*- coding: utf-8 -*-
"""de "auf" before an hour and "Uhr" names a time of day.

"verschiebe den termin von morgen auf fünfzehn uhr" read the whole of
tomorrow and left "auf fünfzehn uhr" in the remainder.  "auf" before an hour
gives a point in time (Duden, "auf", Präposition, Angabe des Zeitpunkts: "das
Taxi ist auf (für) 16 Uhr bestellt").  It is a clock only with "Uhr" after the
hour, so "auf 15 Grad" and "auf 15 Leute" stay no clock.

Anchor: Tuesday 2017-06-27 13:04, so "morgen" is 2017-06-28.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

CLOCKS = [
    ("verschiebe den termin von morgen auf fünfzehn uhr",
     datetime(2017, 6, 28, 15), "verschiebe den termin von"),
    ("morgen auf 15 Uhr", datetime(2017, 6, 28, 15), ""),
    ("morgen auf 3 Uhr nachmittags", datetime(2017, 6, 28, 15), ""),
    ("auf 15 Uhr", datetime(2017, 6, 27, 15), ""),
    ("auf 15:30 Uhr", datetime(2017, 6, 27, 15, 30), ""),
    ("das Taxi ist auf 16 Uhr bestellt", datetime(2017, 6, 27, 16),
     "das Taxi ist bestellt"),
    ("auf 15 Uhr 30", datetime(2017, 6, 27, 15, 30), ""),
    ("auf 7 Uhr 15", datetime(2017, 6, 27, 19, 15), ""),
    ("verschiebe den Termin auf 15 Uhr 30", datetime(2017, 6, 27, 15, 30),
     "verschiebe den Termin"),
    ("auf 15 Uhr dreißig", datetime(2017, 6, 27, 15, 30), ""),
]


@pytest.mark.parametrize("text,instant,remainder", CLOCKS)
def test_auf_with_uhr_is_a_clock(text, instant, remainder):
    found = extract_timespan(text, "de", ANCHOR)
    assert found.span.start.datetime() == instant
    assert found.remainder == remainder


@pytest.mark.parametrize("text", ["auf 15 Grad", "es sind auf 15 Leute",
                                  "auf 15"])
def test_auf_without_uhr_is_no_clock(text):
    assert extract_timespan(text, "de", ANCHOR) is None
