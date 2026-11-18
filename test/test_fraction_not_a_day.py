"""A fraction of a month names no day of it.

"third" is also a fraction: Wiktionary, "third", noun sense 2, "One of three
equal parts of a whole" ("He ate a third of the pie").  A day of the month
takes "the" or no determiner directly before its ordinal.  The anchor is
Saturday 17 October 2026, so the next third of the month is 3 November.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_timespan

ANCHOR = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text", [
    "a full third of the month",
    "a whole fifth of the month",
    "an entire fifth of the month",
    "a solid third of the month",
    "a fair third of the month",
    "a clear third of the month",
    "a complete third of the month",
    "a large third of the month",
    "a mere fifth of the month",
    "an extra fifth of the month",
    "a total third of the month",
    "another third of the month",
    "some third of the month",
    "any third of the month",
    "the first third of the month",
    "the last third of the month",
    "the final third of the month",
    "a full third of march",
    "the middle third of november",
])
def test_a_fraction_names_no_day(text):
    assert extract_timespan(text, "en", ANCHOR) is None


@pytest.mark.parametrize("text, lang, day, rest", [
    ("the third of the month", "en", (2026, 11, 3), ""),
    ("pay rent on the third of the month", "en", (2026, 11, 3), "pay rent"),
    ("the twenty third of the month", "en", (2026, 10, 23), ""),
    ("book a table third of may", "en", (2027, 5, 3), "book a table"),
    ("see you the third of march", "en", (2027, 3, 3), "see you"),
])
def test_a_day_of_the_month_stays(text, lang, day, rest):
    r = extract_timespan(text, lang, ANCHOR)
    assert (r.span.start, r.remainder) == (AstroDate(*day), rest)
