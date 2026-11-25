"""A business-day count past the range ``datetime`` holds names no day.

The count is declined like any impossible date: the readers return ``None``
and ``impossible="raise"`` raises.  A count that fits still reads: with a
Wednesday anchor, 5 * w business days land on the Wednesday 7 * w days later.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import ImpossibleDateError
from chronologia.extract import extract_candidates, extract_timespan

ANCHOR = datetime(2026, 11, 25, 10, 0)

PAST_RANGE = [
    ("de", "30 millionster werktag"),
    ("da", "billionte arbejdsdage"),
    ("nb", "1999 trillioner arbeidsdag"),
    ("en", "in 30000000 business days"),
    # fewer days than the range holds, more business days than it holds
    ("en", "in 2900000 business days"),
    ("en", "30000000 business days ago"),
    ("en", "30000000 business days after christmas"),
    ("en", "the 30000000th business day of july"),
]


@pytest.mark.parametrize("lang,text", PAST_RANGE)
def test_default_mode_reads_nothing(lang, text):
    assert extract_timespan(text, anchor=ANCHOR, lang=lang) is None


@pytest.mark.parametrize("lang,text", PAST_RANGE[:4])
def test_candidates_are_empty(lang, text):
    assert extract_candidates(text, anchor=ANCHOR, lang=lang) == []


@pytest.mark.parametrize("lang,text", PAST_RANGE)
def test_raise_mode_reports_the_count(lang, text):
    with pytest.raises(ImpossibleDateError, match="business day"):
        extract_timespan(text, anchor=ANCHOR, lang=lang, impossible="raise")


@pytest.mark.parametrize("weeks", [1, 100, 20000])
def test_whole_weeks_land_on_the_same_weekday(weeks):
    want = date(2026, 11, 25) + timedelta(days=7 * weeks)
    got = extract_timespan(f"in {5 * weeks} business days", anchor=ANCHOR, lang="en")
    assert (got.span.start.year, got.span.start.month, got.span.start.day) == (
        want.year, want.month, want.day)
