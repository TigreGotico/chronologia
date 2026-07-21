"""Slovenian relative offsets in both directions.

"čez N <unit>" shifts forward, "pred N <unit>" shifts back; both prefix
markers, sign from the marker's declared direction.  Slovene keeps the dual,
so unit nouns take a distinct 2-form (dneva, leti) beside the plural (dni,
let); the past preposition governs the instrumental (pred 5 leti).  Expected
values are independent date arithmetic against the Tuesday 2017-06-27 anchor.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, parse, nomatch


@pytest.mark.parametrize("n,form", [(1, "dan"), (2, "dneva"), (3, "dni"),
                                    (5, "dni"), (10, "dni")])
def test_days_future(n, form):
    assert start(f"čez {n} {form}") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n", [3, 5, 10])
def test_days_past(n):
    assert start(f"pred {n} dnevi") == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "teden"), (2, "tedna"), (3, "tedne"),
                                    (5, "tednov")])
def test_weeks_future(n, form):
    assert start(f"čez {n} {form}") == ad(ANCHOR + timedelta(weeks=n))


@pytest.mark.parametrize("n", [3, 5])
def test_weeks_past(n):
    assert start(f"pred {n} tedni") == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(1, "mesec"), (2, "meseca"), (3, "mesece"),
                                    (5, "mesecev")])
def test_months_future(n, form):
    assert start(f"čez {n} {form}") == ad(ANCHOR + relativedelta(months=n))


@pytest.mark.parametrize("n", [3, 5])
def test_months_past(n):
    assert start(f"pred {n} meseci") == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(1, "leto"), (2, "leti"), (3, "leta"),
                                    (5, "let"), (10, "let")])
def test_years_future(n, form):
    assert start(f"čez {n} {form}") == ad(ANCHOR + relativedelta(years=n))


@pytest.mark.parametrize("n", [2, 5, 10])
def test_years_past(n):
    assert start(f"pred {n} leti") == ad(ANCHOR - relativedelta(years=n))


@pytest.mark.parametrize("n", [5, 10, 30])
def test_minutes_future(n):
    assert start(f"čez {n} minut") == ad(ANCHOR + timedelta(minutes=n))


@pytest.mark.parametrize("phrase,delta", [
    ("čez pet dni", timedelta(days=5)),
    ("čez tri tedne", timedelta(weeks=3)),
    ("čez deset minut", timedelta(minutes=10)),
])
def test_spelled_offset(phrase, delta):
    assert start(phrase) == ad(ANCHOR + delta)


@pytest.mark.parametrize("word,off", [("danes", 0), ("jutri", 1),
                                      ("včeraj", -1)])
def test_named_day(word, off):
    assert start(word) == ad((ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0))


_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("naslednji ponedeljek", _MID + timedelta(days=6)),
    ("naslednji petek", _MID + timedelta(days=3)),
    ("prejšnji petek", _MID - timedelta(days=4)),
    ("prejšnji torek", _MID - timedelta(days=7)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


def test_offset_needs_marker():
    nomatch("pet dni")
    nomatch("dva tedna")
    assert parse("minut") is None
