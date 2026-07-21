"""Bulgarian relative offsets in both directions.

"след N <unit>" shifts forward (after), "преди N <unit>" shifts back
(before); both prefix markers, sign from the marker's declared direction.
Bulgarian has lost the Slavic case system, so unit nouns inflect only for
number (дни, седмици, месеца, години) -- no genitive/instrumental tables.
Values are independent date arithmetic against the Tuesday 2017-06-27 anchor.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, parse, nomatch


@pytest.mark.parametrize("n,form", [(1, "ден"), (2, "дни"), (3, "дни"),
                                    (5, "дни"), (10, "дни")])
def test_days_future(n, form):
    assert start(f"след {n} {form}") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n", [1, 3, 5, 10])
def test_days_past(n):
    form = "ден" if n == 1 else "дни"
    assert start(f"преди {n} {form}") == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "седмица"), (2, "седмици"),
                                    (3, "седмици"), (5, "седмици")])
def test_weeks_future(n, form):
    assert start(f"след {n} {form}") == ad(ANCHOR + timedelta(weeks=n))


@pytest.mark.parametrize("n", [2, 3, 5])
def test_weeks_past(n):
    assert start(f"преди {n} седмици") == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(1, "месец"), (2, "месеца"), (5, "месеца")])
def test_months_future(n, form):
    assert start(f"след {n} {form}") == ad(ANCHOR + relativedelta(months=n))


@pytest.mark.parametrize("n", [2, 5])
def test_months_past(n):
    assert start(f"преди {n} месеца") == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(1, "година"), (2, "години"),
                                    (5, "години"), (10, "години")])
def test_years_future(n, form):
    assert start(f"след {n} {form}") == ad(ANCHOR + relativedelta(years=n))


@pytest.mark.parametrize("n", [2, 5, 10])
def test_years_past(n):
    assert start(f"преди {n} години") == ad(ANCHOR - relativedelta(years=n))


@pytest.mark.parametrize("n,form", [(1, "час"), (2, "часа"), (3, "часа")])
def test_hours_future(n, form):
    assert start(f"след {n} {form}") == ad(ANCHOR + timedelta(hours=n))


@pytest.mark.parametrize("n", [5, 10, 30])
def test_minutes_future(n):
    assert start(f"след {n} минути") == ad(ANCHOR + timedelta(minutes=n))


@pytest.mark.parametrize("phrase,delta", [
    ("след пет дни", timedelta(days=5)),
    ("след три седмици", timedelta(weeks=3)),
    ("след десет минути", timedelta(minutes=10)),
])
def test_spelled_offset(phrase, delta):
    assert start(phrase) == ad(ANCHOR + delta)


@pytest.mark.parametrize("word,off", [("днес", 0), ("утре", 1),
                                      ("вчера", -1), ("вдругиден", 2)])
def test_named_day(word, off):
    assert start(word) == ad((ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0))


_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("следващия понеделник", _MID + timedelta(days=6)),
    ("следващия петък", _MID + timedelta(days=3)),
    ("миналия петък", _MID - timedelta(days=4)),
    ("миналия вторник", _MID - timedelta(days=7)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


def test_offset_needs_marker():
    nomatch("пет дни")
    nomatch("две седмици")
    assert parse("минути") is None
