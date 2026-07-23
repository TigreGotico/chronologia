"""Multi-mention: every non-overlapping temporal mention in one sentence.

The contract is ``extract_timespans(text, "en", anchor)`` -- a list of
:class:`TimeMention` in reading order, where the single-span edge would return
only the first.  Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

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


# --- ranges are ONE mention, not shredded endpoints (Defect B) -------------
# A "from A to B" / "between A and B" range must survive multi-mention
# extraction as a single range span -- the same span the single-span edge
# resolves -- while a bare "and"/"or" list of dates stays several mentions.
@pytest.mark.parametrize("text,count", [
    # a range followed by a boundary ("then") + a loose day: range + day = 2
    ("from monday to friday, then next tuesday", 2),
    # a between-led range spanning the whole sentence: one mention
    ("between june 5th and june 12th", 1),
    # a bare clock range: one mention
    ("from 9am to 5pm", 1),
    # bare "and" across two clauses is a LIST, not a range: stays 2
    ("the meeting is june 5th and the deadline is june 12th", 2),
    # bare "and" between two bare weekdays is a LIST: stays 2
    ("I'm free monday and wednesday", 2),
    # bare "or" is a list: stays 2 (regression)
    ("meet friday at 3 or monday at noon", 2),
])
def test_range_mention_count(text, count):
    assert len(mentions(text)) == count


def test_from_to_range_is_one_span():
    # anchor Tue 2017-06-27: monday -> 07-03, friday rolls into the same week
    # -> range [07-03, 07-08); "then next tuesday" is a separate mention (07-04)
    ms = mentions("from monday to friday, then next tuesday")
    assert len(ms) == 2
    assert ms[0].text == "from monday to friday"
    assert ms[0].span.start == ad(datetime(2017, 7, 3))
    assert ms[0].span.end == ad(datetime(2017, 7, 8))
    assert ms[1].span.start == ad(datetime(2017, 7, 4))


def test_between_and_range_is_one_span():
    # june 5th/12th are past on 06-27, so prefer-future flings both to 2018;
    # the range runs from june 5 start to june 12's day-end -> [06-05, 06-13)
    ms = mentions("between june 5th and june 12th")
    assert len(ms) == 1
    assert ms[0].span.start == ad(datetime(2018, 6, 5))
    assert ms[0].span.end == ad(datetime(2018, 6, 13))


def test_clock_range_is_one_span():
    ms = mentions("from 9am to 5pm")
    assert len(ms) == 1
    assert ms[0].span.start == ad(datetime(2017, 6, 28, 9, 0))
    assert ms[0].span.end == ad(datetime(2017, 6, 28, 17, 1))


def test_range_mention_matches_single_span_edge():
    # the plural range must be the *identical* span the single-span edge yields
    from chronologia.extract import extract_timespan
    for text in ("between june 5th and june 12th", "from 9am to 5pm"):
        ms = mentions(text)
        assert len(ms) == 1
        assert ms[0].span == extract_timespan(text, LANG, ANCHOR).span
