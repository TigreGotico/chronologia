"""Croatian relative offsets in both directions.

"za N <unit>" shifts forward, "prije N <unit>" shifts back; both are prefix
markers and the sign is the marker's declared direction.  Unit nouns carry
the genitive the count governs (dana, tjedna/tjedana, mjeseca/mjeseci,
godine/godina).  Expected values are independent date arithmetic against the
Tuesday 2017-06-27 13:04 anchor.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, parse, nomatch


@pytest.mark.parametrize("n", [1, 2, 3, 5, 10])
def test_days_future(n):
    form = "dan" if n == 1 else "dana"
    assert start(f"za {n} {form}") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n", [1, 3, 5])
def test_days_past(n):
    form = "dan" if n == 1 else "dana"
    assert start(f"prije {n} {form}") == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "tjedan"), (2, "tjedna"), (3, "tjedna"),
                                    (5, "tjedana")])
def test_weeks_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(2, "tjedna"), (5, "tjedana")])
def test_weeks_past(n, form):
    assert start(f"prije {n} {form}") == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(1, "mjesec"), (2, "mjeseca"),
                                    (5, "mjeseci")])
def test_months_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(2, "mjeseca"), (5, "mjeseci")])
def test_months_past(n, form):
    assert start(f"prije {n} {form}") == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(1, "godina"), (2, "godine"),
                                    (5, "godina"), (10, "godina")])
def test_years_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + relativedelta(years=n))


@pytest.mark.parametrize("n,form", [(2, "godine"), (5, "godina")])
def test_years_past(n, form):
    assert start(f"prije {n} {form}") == ad(ANCHOR - relativedelta(years=n))


@pytest.mark.parametrize("n", [5, 10, 30])
def test_minutes_future(n):
    assert start(f"za {n} minuta") == ad(ANCHOR + timedelta(minutes=n))


@pytest.mark.parametrize("phrase,delta", [
    ("za pet dana", timedelta(days=5)),
    ("za tri tjedna", timedelta(weeks=3)),
    ("za deset minuta", timedelta(minutes=10)),
])
def test_spelled_offset(phrase, delta):
    assert start(phrase) == ad(ANCHOR + delta)


@pytest.mark.parametrize("word,off", [("danas", 0), ("sutra", 1),
                                      ("jučer", -1), ("prekosutra", 2),
                                      ("prekjučer", -2)])
def test_named_day(word, off):
    assert start(word) == ad((ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0))


_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("sljedeći ponedjeljak", _MID + timedelta(days=6)),
    ("sljedeći petak", _MID + timedelta(days=3)),
    ("prošli petak", _MID - timedelta(days=4)),
    ("prošli utorak", _MID - timedelta(days=7)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


def test_offset_needs_marker():
    nomatch("pet dana")
    nomatch("dva tjedna")
    assert parse("minuta") is None
