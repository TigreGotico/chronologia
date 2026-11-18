"""A date with "onwards" after it is the open span from the start of that date.

"2019 onwards" includes 2019 and has no end, as ruling 33 reads "after X"
with the start moved to the start of X.  Sources for the markers are in each
locale's ``marker_onwards.voc``.  The anchor is Monday 16 November 2026: the
next March is March 2027, tomorrow is 17 November.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_candidates, extract_timespan

ANCHOR = datetime(2026, 11, 16, 12, 0)


@pytest.mark.parametrize("text, lang, start, rest", [
    ("2019 onwards", "en", (2019, 1, 1), ""),
    ("2019 onward", "en", (2019, 1, 1), ""),
    ("from 2019 onwards", "en", (2019, 1, 1), ""),
    ("i lived there from 2019 onwards", "en", (2019, 1, 1), "i lived there"),
    ("2019 onwards we grew", "en", (2019, 1, 1), "we grew"),
    ("march onwards", "en", (2027, 3, 1), ""),
    ("tomorrow onwards", "en", (2026, 11, 17), ""),
    ("2019 em diante", "pt", (2019, 1, 1), ""),
    ("de 2019 em diante", "pt", (2019, 1, 1), ""),
    ("de amanhã em diante", "pt", (2026, 11, 17), ""),
    ("de 2019 en adelante", "es", (2019, 1, 1), ""),
    ("dal 2019 in poi", "it", (2019, 1, 1), ""),
    ("da domani in poi", "it", (2026, 11, 17), ""),
])
def test_onwards_opens_the_span_at_the_start(text, lang, start, rest):
    r = extract_timespan(text, lang, ANCHOR)
    assert (r.span.start, r.span.open_end, r.remainder) == (
        AstroDate(*start), True, rest)


def test_the_first_candidate_is_the_open_span():
    top = extract_candidates("2019 onwards", "en", ANCHOR)[0]
    assert (top.span.start, top.span.open_end, top.remainder) == (
        AstroDate(2019, 1, 1), True, "")


def test_from_without_onwards_stays_closed_at_now():
    r = extract_timespan("from 2019", "en", ANCHOR)
    assert (r.span.start, r.span.end, r.span.open_end) == (
        AstroDate(2019, 1, 1), AstroDate(2026, 11, 16, 12, 0), False)
