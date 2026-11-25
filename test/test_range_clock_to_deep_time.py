"""A range from a clock word to a deep-time end raises nothing.

A reversed range cannot be rolled by a day when its end lies millions of years
back, so it reads as the interval between the two ends, like "2020 to the
devonian".  The Devonian began about 419 million years ago.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_candidates, extract_timespan

ANCHOR = datetime(2026, 11, 25, 10, 0)

#: (language, clock-to-period phrase, the same range written period first)
RANGES = [
    ("nl", "middag t/m devoon", "devoon t/m middag"),
    ("en", "noon to the devonian", "the devonian to noon"),
    ("en", "3pm until the devonian", "the devonian until 3pm"),
    ("de", "mittag bis devon", "devon bis mittag"),
    ("da", "middag til devon", "devon til middag"),
    ("nb", "middag til og med devon", "devon til og med middag"),
    ("sv", "middag till devon", "devon till middag"),
    ("fr", "midi jusqu'au devonian", "devonian jusqu'au midi"),
    ("it", "mezzogiorno fino al devonian", "devonian fino al mezzogiorno"),
    ("ro", "amiaza până la devonian", "devonian până la amiaza"),
]


def parts(span):
    start, end = span.span.start, span.span.end
    return start.year, (end.year, end.month, end.day, end.hour)


@pytest.mark.parametrize("lang,text,reversed_text", RANGES)
def test_range_to_a_period_reads(lang, text, reversed_text):
    got = extract_timespan(text, anchor=ANCHOR, lang=lang)
    year, end = parts(got)
    assert -430_000_000 < year < -410_000_000
    assert end[:3] == (2026, 11, 25)
    assert end[3] in (12, 15)
    assert extract_candidates(text, anchor=ANCHOR, lang=lang)


@pytest.mark.parametrize("lang,text,reversed_text", RANGES)
def test_range_reads_as_the_period_first_range(lang, text, reversed_text):
    assert parts(extract_timespan(text, anchor=ANCHOR, lang=lang)) == parts(
        extract_timespan(reversed_text, anchor=ANCHOR, lang=lang))


def test_range_to_a_point_in_deep_time_leaves_each_side_alone():
    got = extract_timespan("noon to 10 million years ago", anchor=ANCHOR, lang="en")
    assert (got.span.start.year, got.span.start.month, got.span.start.day,
            got.span.start.hour) == (2026, 11, 25, 12)
    assert got.remainder == "to 10 million years ago"
