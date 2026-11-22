"""Russian "в N-ом часу": the N-th hour of the clock face, from N-1 to N.

"в восьмом часу" is the span 7:00 to 8:00, counted as "в половине восьмого"
(7:30) is: the eighth hour begins at seven.  A day-period word fixes the half
of the day ("вечера" 19:00 to 20:00, "утра" 07:00 to 08:00); with none, the
hour takes the next of its two twelve-hour readings after the anchor, as a
lone spoken hour does (docs/rulings.md, ruling 17).  The word "часу" belongs
to the phrase.  Hours run first to twelfth.  The gold values are hand
arithmetic on the rule, not engine output.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_event

from ._corpus import ad, nomatch, parse

#: 02:00 on a Sunday: every morning hour is still ahead, midnight has passed.
EARLY = datetime(2026, 11, 22, 2, 0)
#: 13:30 the same day: every morning hour and noon have passed.
LATE = datetime(2026, 11, 22, 13, 30)


def _hour(day, hour):
    """The hour that starts at ``hour`` o'clock on ``day`` (hour 24 is the
    next midnight)."""
    start = datetime(2026, 11, day) + timedelta(hours=hour)
    return ad(start), ad(start + timedelta(hours=1))


@pytest.mark.parametrize("text,gold", [
    ("в первом часу дня", _hour(22, 12)),
    ("в первом часу ночи", _hour(23, 0)),
    ("в седьмом часу утра", _hour(22, 6)),
    ("в седьмом часу вечера", _hour(22, 18)),
    ("в восьмом часу утра", _hour(22, 7)),
    ("в восьмом часу вечера", _hour(22, 19)),
    ("в двенадцатом часу дня", _hour(22, 11)),
    ("в двенадцатом часу ночи", _hour(22, 23)),
])
def test_day_period_fixes_the_half_of_the_day(text, gold):
    r = parse(text, EARLY)
    assert r is not None
    assert (r.span.start, r.span.end) == gold
    assert r.remainder == ""


@pytest.mark.parametrize("text,anchor,gold", [
    ("в первом часу", EARLY, _hour(22, 12)),
    ("в седьмом часу", EARLY, _hour(22, 6)),
    ("в восьмом часу", EARLY, _hour(22, 7)),
    ("в двенадцатом часу", EARLY, _hour(22, 11)),
    ("в первом часу", LATE, _hour(23, 0)),
    ("в седьмом часу", LATE, _hour(22, 18)),
    ("в восьмом часу", LATE, _hour(22, 19)),
    ("в двенадцатом часу", LATE, _hour(22, 23)),
])
def test_bare_hour_takes_the_next_twelve_hour_reading(text, anchor, gold):
    r = parse(text, anchor)
    assert r is not None
    assert (r.span.start, r.span.end) == gold
    assert r.remainder == ""


def test_anchor_inside_the_hour_picks_the_reading_by_the_hour_start():
    inside = datetime(2026, 11, 22, 7, 30)
    r = parse("в восьмом часу", inside)
    assert (r.span.start, r.span.end) == _hour(22, 19)


@pytest.mark.parametrize("text,gold", [
    ("вечером в восьмом часу", _hour(22, 19)),
    ("утром в восьмом часу", _hour(22, 7)),
])
def test_day_period_word_before_the_phrase_keeps_the_hour_width(text, gold):
    r = parse(text, EARLY)
    assert (r.span.start, r.span.end) == gold
    assert r.remainder == ""


def test_inside_a_sentence():
    r = parse("встретимся в восьмом часу вечера", EARLY)
    assert (r.span.start, r.span.end) == _hour(22, 19)
    assert r.remainder == "встретимся"


def test_event_summary_keeps_the_other_words():
    event = extract_event("встретимся в восьмом часу вечера", "ru", EARLY)
    assert event.summary == "встретимся"
    assert (event.span.start, event.span.end) == _hour(22, 19)


def test_named_day_keeps_the_hour_width():
    r = parse("завтра в восьмом часу вечера", EARLY)
    assert (r.span.start, r.span.end) == _hour(23, 19)
    assert r.remainder == ""


def test_cardinal_clock_stays_a_minute():
    r = parse("в 8 часов вечера", EARLY)
    assert r.span.start == ad(datetime(2026, 11, 22, 20, 0))
    assert r.span.end == ad(datetime(2026, 11, 22, 20, 1))


def test_ordinal_that_agrees_with_another_noun_is_not_a_clock():
    nomatch("в восьмом классе", EARLY)


@pytest.mark.parametrize("text,gold", [
    ("в 8-м часу вечера", _hour(22, 19)),
    ("в 8-ом часу вечера", _hour(22, 19)),
    ("в 8-м часу утра", _hour(22, 7)),
    ("в 1-м часу ночи", _hour(23, 0)),
    ("в 1-м часу дня", _hour(22, 12)),
    ("в 12-м часу дня", _hour(22, 11)),
    ("в 12-м часу ночи", _hour(22, 23)),
    ("в 8-м часу", _hour(22, 7)),
])
def test_digit_ordinal_reads_like_the_spelled_ordinal(text, gold):
    r = parse(text, EARLY)
    assert r is not None
    assert (r.span.start, r.span.end) == gold
    assert r.remainder == ""


@pytest.mark.parametrize("text,gold", [
    ("часу в восьмом вечера", _hour(22, 19)),
    ("часу в восьмом утра", _hour(22, 7)),
    ("часу в двенадцатом", _hour(22, 11)),
    ("часу в 8-м вечера", _hour(22, 19)),
])
def test_inverted_order_reads_the_same_hour_span(text, gold):
    r = parse(text, EARLY)
    assert r is not None
    assert (r.span.start, r.span.end) == gold
    assert r.remainder == ""


def test_inside_a_sentence_with_a_digit_ordinal():
    r = parse("встретимся в 8-м часу вечера", EARLY)
    assert (r.span.start, r.span.end) == _hour(22, 19)
    assert r.remainder == "встретимся"


def test_bare_cardinal_before_chasu_is_not_an_hour_span():
    nomatch("в 8 часу вечера", EARLY)


def test_k_chasu_is_not_an_hour_span():
    nomatch("к часу дня", EARLY)
