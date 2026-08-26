"""Durations, and the words that are counters rather than calendar labels."""
import pytest

from chronologia import extract_duration


def dur(text):
    return extract_duration(text, "ko")


@pytest.mark.parametrize("text,seconds", [
    ("3일", 3 * 86400),
    ("2주", 2 * 7 * 86400),
    ("45분", 45 * 60),
    ("30초", 30),
    ("5시간", 5 * 3600),
    ("일주일", 7 * 86400),
])
def test_a_counted_duration(text, seconds):
    r = dur(text)
    assert r is not None, text
    assert r[0].total_seconds() == seconds


@pytest.mark.parametrize("text", ["3월", "12월"])
def test_the_month_label_makes_no_duration(text):
    """월 numbers the months of the year; it never counts them.  Reading it
    as a count is the single most damaging confusion available here, because
    both words are grammatical in the same slot."""
    assert dur(text) is None


@pytest.mark.parametrize("text", ["세 시간", "다섯 시간", "삼 시간"])
def test_a_spelled_hour_count_is_not_read(text):
    """The sources consulted state the native/Sino split for telling the
    TIME -- the hour, minute and second of a clock -- and for the calendar
    fields.  Neither states which series counts a span of 시간 hours, so
    neither is folded there and only the digit form is read."""
    assert dur(text) is None
