"""Multi-mention: every non-overlapping temporal mention in one sentence.

The contract is ``extract_timespans(text, "en", anchor)`` -- a list of
:class:`TimeMention` in reading order, where the single-span edge would return
only the first.  Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_timespans
from ._corpus import ANCHOR, ad

LANG = "en"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


@pytest.mark.parametrize("text,count", [
    ("meet friday at 3 or monday at noon", 2),
    ("june 5th 2027 and july 2028", 2),
    ("tomorrow or next week", 2),
    ("yesterday, today and tomorrow", 3),
    ("3pm and 5pm", 2),
    ("just tomorrow", 1),
    ("call me on monday", 1),
    ("nothing temporal here", 0),
])
def test_mention_count(text, count):
    assert len(mentions(text)) == count


def test_two_datetimes_compose_and_order():
    ms = mentions("meet friday at 3 or monday at noon")
    assert [m.text for m in ms] == ["friday at 3", "monday at noon"]
    # friday 2017-06-30 03:00, monday 2017-07-03 12:00 (hand-derived)
    assert ms[0].span.start == ad((ANCHOR + timedelta(days=3)).replace(
        hour=3, minute=0))
    assert ms[1].span.start == ad((ANCHOR + timedelta(days=6)).replace(
        hour=12, minute=0))


def test_token_extents_are_reported():
    ms = mentions("june 5th 2027 and july 2028")
    assert ms[0].token_span == (0, 3)
    assert ms[1].token_span == (4, 6)


def test_three_named_days_in_order():
    ms = mentions("yesterday, today and tomorrow")
    starts = [m.span.start.day for m in ms]
    assert starts == [26, 27, 28]
