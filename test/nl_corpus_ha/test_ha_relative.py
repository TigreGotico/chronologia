"""Named days, counted offsets, and the deictic period words.

An offset in Hausa is the unit noun, its count, and a trailing relative
clause -- "kwanaki uku da suka gabata" -- for the past, and a leading *cikin*
or *bayan* for the future.  The span a counted offset returns is one unit
wide, starting at the offset instant.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, day, month_span, nomatch, start_end, year_span


def _shift_months(dt, n):
    """dt moved n calendar months, computed without the parser."""
    total = (dt.year * 12 + dt.month - 1) + n
    return dt.replace(year=total // 12, month=total % 12 + 1)


def _delta(kind, n):
    """The anchor moved n units, and that instant plus one unit."""
    if kind == "month":
        return _shift_months(ANCHOR, n), _shift_months(ANCHOR, n + 1)
    if kind == "year":
        return (ANCHOR.replace(year=ANCHOR.year + n),
                ANCHOR.replace(year=ANCHOR.year + n + 1))
    unit = {"second": timedelta(seconds=1), "minute": timedelta(minutes=1),
            "hour": timedelta(hours=1), "day": timedelta(days=1),
            "week": timedelta(weeks=1)}[kind]
    return ANCHOR + unit * n, ANCHOR + unit * (n + 1)


def offset(kind, n):
    lo, hi = _delta(kind, n)
    return ad(lo), ad(hi)


@pytest.mark.parametrize("text,expected", [
    ("yau", (2027, 5, 12)),
    ("gobe", (2027, 5, 13)),
    ("jiya", (2027, 5, 11)),
    ("shekaranjiya", (2027, 5, 10)),
])
def test_the_named_days(text, expected):
    assert start_end(text) == day(*expected)


PAST = [
    ("dakiku talatin da suka gabata", "second", -30),
    ("mintuna goma da suka gabata", "minute", -10),
    ("mintuna sha biyar da suka gabata", "minute", -15),
    ("awanni uku da suka gabata", "hour", -3),
    ("kwanaki uku da suka gabata", "day", -3),
    ("kwanaki biyar da suka gabata", "day", -5),
    ("makonni biyu da suka gabata", "week", -2),
    ("watanni uku da suka gabata", "month", -3),
    ("shekaru biyu da suka gabata", "year", -2),
    ("shekaru goma sha ɗaya da suka gabata", "year", -11),
    ("shekaru ɗari da suka gabata", "year", -100),
]


@pytest.mark.parametrize("text,kind,n", PAST)
def test_the_trailing_past_clause_counts_backwards(text, kind, n):
    assert start_end(text) == offset(kind, n)


FUTURE = [
    ("cikin kwanaki biyu", "day", 2),
    ("cikin awanni uku", "hour", 3),
    ("cikin mintuna arba'in da biyar", "minute", 45),
    ("cikin makonni biyu", "week", 2),
    ("a cikin watanni uku", "month", 3),
    ("a cikin shekaru huɗu", "year", 4),
    ("bayan kwanaki uku", "day", 3),
    ("bayan shekaru huɗu", "year", 4),
]


@pytest.mark.parametrize("text,kind,n", FUTURE)
def test_the_leading_marker_counts_forwards(text, kind, n):
    assert start_end(text) == offset(kind, n)


@pytest.mark.parametrize("text,expected", [
    ("wannan watan", month_span(2027, 5)),
    ("watan da ya gabata", month_span(2027, 4)),
    ("wata na gaba", month_span(2027, 6)),
    ("wata mai zuwa", month_span(2027, 6)),
    ("wannan shekarar", year_span(2027)),
    ("shekarar da ta gabata", year_span(2026)),
    ("shekara mai zuwa", year_span(2028)),
])
def test_the_deictic_calendar_periods(text, expected):
    assert start_end(text) == expected


@pytest.mark.parametrize("text,delta_weeks", [
    ("wannan satin", 0),
    ("satin da ya gabata", -1),
    ("sati na gaba", 1),
    ("sati mai zuwa", 1),
])
def test_the_deictic_weeks_are_calendar_weeks(text, delta_weeks):
    monday = (datetime(ANCHOR.year, ANCHOR.month, ANCHOR.day)
              - timedelta(days=ANCHOR.weekday())
              + timedelta(weeks=delta_weeks))
    assert start_end(text) == (ad(monday), ad(monday + timedelta(weeks=1)))


@pytest.mark.parametrize("text", ["kwanaki", "shekaru", "makonni", "awanni"])
def test_a_bare_unit_without_a_count_is_not_an_offset(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["da ya gabata", "da suka gabata", "cikin",
                                  "na gaba", "mai zuwa", "wannan"])
def test_a_lone_marker_is_not_a_date(text):
    nomatch(text)
