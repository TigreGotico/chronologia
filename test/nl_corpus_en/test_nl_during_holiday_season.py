""""during" and "in" before a holiday or a season belong to it.

"during christmas" and "in summer" name the holiday and the season.  Before
this, the reference read and "during" or "in" stayed in the remainder.

Meteorological summer is June, July and August (NOAA NCEI,
"Meteorological Versus Astronomical Seasons").  Christmas is 25 December.
Anchor 16 November 2026.
"""
from datetime import datetime

import pytest

from ._corpus import parse

ANCHOR = datetime(2026, 11, 16, 12, 0)
SUMMER_2027 = (datetime(2027, 6, 1), datetime(2027, 9, 1))
CHRISTMAS_2026 = (datetime(2026, 12, 25), datetime(2026, 12, 26))


@pytest.mark.parametrize("text, bounds, remainder", [
    ("the shop is closed during christmas", CHRISTMAS_2026,
     "the shop is closed"),
    ("during christmas 2027", (datetime(2027, 12, 25), datetime(2027, 12, 26)),
     ""),
    ("we go to the beach during next summer", SUMMER_2027,
     "we go to the beach"),
    ("in the summer of 2027", SUMMER_2027, ""),
])
def test_during_or_in_reads_with_the_reference(text, bounds, remainder):
    span, rest = parse(text, ANCHOR)
    assert (span.start, span.end) == bounds
    assert rest == remainder


@pytest.mark.parametrize("text, bare", [
    ("in summer", "summer"),
    ("during the summer", "the summer"),
])
def test_in_a_bare_season_reads_as_the_season(text, bare):
    # the bare season keeps its own reading; only the word before it moves
    span, rest = parse(text, ANCHOR)
    assert span == parse(bare, ANCHOR)[0]
    assert rest == ""


def test_during_before_a_relative_marker_reads_with_the_holiday():
    span, rest = parse("during next christmas", ANCHOR)
    assert (span.start, span.end) == CHRISTMAS_2026
    assert rest == ""
