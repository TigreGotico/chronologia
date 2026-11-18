"""A numeral alone is a candidate, not a reading.

Ruling 34 of the chronologia disagreement rulings: a numeral with no clock
marker, no unit and no year cue is not a date in ``extract_timespan``, as
ruling 2 keeps a bare number from being a clock.  ``extract_candidates``
lists its year reading, ranked low.  A lone numeral is the whole text: a
year with any other word ("in", a year word, a month, "before", "2400
people came") still reads.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_candidates, extract_timespan


@pytest.mark.parametrize("lang, text, anchor", [
    ("en", "2400", datetime(2017, 6, 27, 13, 4)),
    ("en", "2400", datetime(2117, 9, 3, 13, 30)),
    ("nl", "2400", datetime(2017, 6, 27, 13, 4)),
    ("nl", "2400", datetime(1998, 1, 1)),
    ("en", "1990", datetime(2017, 6, 27, 13, 4)),
    ("pt", "1990", datetime(2017, 6, 27, 13, 4)),
])
def test_a_lone_numeral_is_no_date(lang, text, anchor):
    assert extract_timespan(text, lang, anchor) is None


def test_the_year_stays_a_candidate():
    spans = [c.span for c in
             extract_candidates("2400", "en", datetime(2017, 6, 27, 13, 4))]
    assert (AstroDate(2400, 1, 1), AstroDate(2401, 1, 1)) in [
        (s.start, s.end) for s in spans]


@pytest.mark.parametrize("text, year", [
    ("in 2400", 2400),
    ("the year 2400", 2400),
    ("june 2400", 2400),
    ("christmas 2020", 2020),
    # any other word makes the numeral part of a phrase
    ("2400 people came", 2400),
])
def test_a_year_with_a_cue_still_reads(text, year):
    span, _ = extract_timespan(text, "en", datetime(2017, 6, 27, 13, 4))
    assert span.start.year == year


def test_before_a_lone_year_still_reads():
    span, rest = extract_timespan("before 2030", "en", datetime(2017, 6, 27, 13, 4))
    assert (span.start, rest) == (AstroDate(2017, 6, 27, 13, 4), "")


@pytest.mark.parametrize("lang, text", [
    ("en", "2019 onwards"),
    ("pt", "2019 em diante"),
    ("es", "de 2019 en adelante"),
])
def test_a_year_with_onwards_is_the_open_span(lang, text):
    r = extract_timespan(text, lang, datetime(2026, 11, 16, 12, 0))
    assert (r.span.start, r.span.open_end, r.remainder) == (
        AstroDate(2019, 1, 1), True, "")
