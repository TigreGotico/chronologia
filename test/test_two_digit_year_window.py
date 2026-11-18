"""A two-digit year takes ICU's default century window around the anchor.

ICU4J SimpleDateFormat reads an abbreviated year "within 80 years before and 20
years after the time the SimpleDateFormat instance is created", so a two-digit
year reads in the hundred years from 80 years before the anchor to 19 years
after it.  Anchor 3 September 2117: the window
is 2037 to 2136, so "20" is 2120, "36" is 2136 and "37" is 2037.  Anchor 1850:
the window is 1770 to 1869, so "69" is 1869 and "70" is 1770.  Anchor 2026:
the window is 1946 to 2045, so "20" is 2020.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan


def _start(text, lang, anchor):
    span, rest = extract_timespan(text, lang, anchor)
    assert rest == ""
    return (span.start.year, span.start.month, span.start.day)


@pytest.mark.parametrize("lang", ["fr", "da", "sv", "pt", "es", "de"])
def test_a_slash_date_said_in_2117_reads_the_next_century(lang):
    text = "15.06.20" if lang == "de" else "15/06/20"
    assert _start(text, lang, datetime(2117, 9, 3, 13, 30)) == (2120, 6, 15)


@pytest.mark.parametrize("anchor, yy, year", [
    (datetime(2117, 9, 3, 13, 30), 20, 2120),
    (datetime(2117, 9, 3, 13, 30), 36, 2136),
    (datetime(2117, 9, 3, 13, 30), 37, 2037),
    (datetime(1850, 1, 1), 69, 1869),
    (datetime(1850, 1, 1), 70, 1770),
    (datetime(2026, 11, 18), 20, 2020),
    (datetime(2026, 11, 18), 45, 2045),
    (datetime(2026, 11, 18), 46, 1946),
])
def test_an_apostrophe_year_reads_inside_the_window(anchor, yy, year):
    assert _start(f"the summer of '{yy:02d}", "en", anchor)[0] == year
