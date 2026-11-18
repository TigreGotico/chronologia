"""A bare "before X" runs from the anchor to the start of X (ruling 29).

"Before" means "earlier than" (Wiktionary, "before", preposition: "Earlier
than (in time)."), so X itself is not in the span.  "until X" keeps X.  The
golds are calendar arithmetic: Christmas 2026 is 25 December, 2026-10-17 is a
Saturday so the next Friday is 23 October, and 2026-11-16 is a Monday.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_candidates, extract_timespan

SEPT = datetime(2026, 9, 25, 12, 0)
SAT = datetime(2026, 10, 17, 12, 0)
MON = datetime(2026, 11, 16, 12, 0)


@pytest.mark.parametrize("lang, text, anchor, end", [
    ("fr", "avant noël", SEPT, datetime(2026, 12, 25)),
    ("en", "before christmas", SEPT, datetime(2026, 12, 25)),
    ("sv", "före jul", SEPT, datetime(2026, 12, 25)),
    ("pt", "antes do natal", SEPT, datetime(2026, 12, 25)),
    ("en", "before friday", SAT, datetime(2026, 10, 23)),
    ("en", "before may 13", MON, datetime(2027, 5, 13)),
    ("de", "vor Weihnachten", SEPT, datetime(2026, 12, 25)),
])
def test_before_x_ends_when_x_begins(lang, text, anchor, end):
    span, rest = extract_timespan(text, lang, anchor)
    assert (span.start, span.end, rest) == (AstroDate.from_datetime(anchor),
                                            AstroDate.from_datetime(end), "")


def test_the_first_candidate_agrees():
    first = extract_candidates("before christmas", "en", SEPT, limit=3)[0]
    assert (first.span.start, first.span.end) == (
        AstroDate.from_datetime(SEPT), AstroDate.from_datetime(datetime(2026, 12, 25)))


def test_until_x_still_takes_x_in():
    span, _ = extract_timespan("until christmas", "en", SEPT)
    assert span.end == AstroDate.from_datetime(datetime(2026, 12, 26))


def test_before_a_day_already_begun_is_refused():
    # Monday 16 November 12:00: "monday" is today, which began at 00:00
    assert extract_timespan("before monday", "en", MON) is None


@pytest.mark.parametrize("lang, text, marker", [
    ("en", "before monday", "before"),
    ("ru", "до понедельника", "до"),
])
def test_no_candidate_reads_the_day_and_leaves_the_marker(lang, text, marker):
    assert [c.span for c in extract_candidates(text, lang, MON)
            if c.remainder == marker] == []
