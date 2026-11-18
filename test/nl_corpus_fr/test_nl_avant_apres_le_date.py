""""après le 13 mai" and "avant le 13 mai" read as en "after may 13" does.

A bare "after X" names an open future from the end of X: a ``DateSpan``
with ``open_end``, never X itself.  "avant X" (before X)
is the range from now to the start of X, as en "before may 13" is (ruling 29).

The French date takes its article, "le 13 mai", so the article belongs to
the date and the marker is the only word left over.  The gold is plain date
arithmetic from the anchor, 16 November 2026: the next 13 May is in 2027.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

from ._corpus import parse

ANCHOR = datetime(2026, 11, 16, 12, 0)


@pytest.mark.parametrize("fr, en, start", [
    ("après le 13 mai", "after may 13", datetime(2027, 5, 14)),
    ("après le 1er juin", "after june 1st", datetime(2027, 6, 2)),
])
def test_after_a_date_is_open_as_in_english(fr, en, start):
    for span, rest in (parse(fr, ANCHOR), extract_timespan(en, "en", ANCHOR)):
        assert (span.start, span.open_end) == (start, True)
        assert rest == ""


@pytest.mark.parametrize("text, end", [
    ("avant le 13 mai", datetime(2027, 5, 13)),
    ("avant le 1er juin", datetime(2027, 6, 1)),
])
def test_before_a_date_runs_from_now_to_its_start(text, end):
    span, rest = parse(text, ANCHOR)
    assert (span.start, span.end) == (ANCHOR, end)
    assert rest == ""


def test_before_a_past_date_is_refused():
    # "avant le 13 mai 2020" names no future to run to
    assert parse("avant le 13 mai 2020", ANCHOR) is None


def test_a_date_with_its_article_alone_is_unchanged():
    span, rest = parse("le 13 mai", ANCHOR)
    assert (span.start, span.end) == (datetime(2027, 5, 13),
                                      datetime(2027, 5, 14))
    assert rest == ""
