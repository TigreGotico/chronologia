"""Ukrainian relative offsets in both directions.

"через N <unit>" shifts forward (prefix marker), "N <unit> тому" shifts back
(suffix marker).  Unit nouns carry the case the count governs (nominative
plural 2-4, genitive plural 5+: тижні/тижнів, місяці/місяців, роки/років).
Values mirror the deposited uk period-offset golds against the Tuesday
2017-06-27 13:04 anchor.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, parse, nomatch


@pytest.mark.parametrize("n,form", [(1, "день"), (2, "дні"), (3, "дні"),
                                    (5, "днів"), (10, "днів")])
def test_days_future(n, form):
    assert start(f"через {n} {form}") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "день"), (3, "дні"), (5, "днів")])
def test_days_past(n, form):
    assert start(f"{n} {form} тому") == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "тиждень"), (2, "тижні"), (3, "тижні"),
                                    (5, "тижнів")])
def test_weeks_future(n, form):
    assert start(f"через {n} {form}") == ad(ANCHOR + timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(2, "тижні"), (3, "тижнів"), (5, "тижнів")])
def test_weeks_past(n, form):
    assert start(f"{n} {form} тому") == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(1, "місяць"), (2, "місяці"),
                                    (5, "місяців")])
def test_months_future(n, form):
    assert start(f"через {n} {form}") == ad(ANCHOR + relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(2, "місяці"), (5, "місяців")])
def test_months_past(n, form):
    assert start(f"{n} {form} тому") == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(1, "рік"), (2, "роки"), (5, "років"),
                                    (10, "років")])
def test_years_future(n, form):
    assert start(f"через {n} {form}") == ad(ANCHOR + relativedelta(years=n))


@pytest.mark.parametrize("n,form", [(2, "роки"), (5, "років")])
def test_years_past(n, form):
    assert start(f"{n} {form} тому") == ad(ANCHOR - relativedelta(years=n))


@pytest.mark.parametrize("n", [5, 10, 30, 45])
def test_minutes_future(n):
    assert start(f"через {n} хвилин") == ad(ANCHOR + timedelta(minutes=n))


@pytest.mark.parametrize("phrase,delta", [
    ("через п'ять днів", timedelta(days=5)),
    ("через три тижні", timedelta(weeks=3)),
    ("через десять хвилин", timedelta(minutes=10)),
])
def test_spelled_offset(phrase, delta):
    assert start(phrase) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,delta", [
    ("зустрінемось через 3 дні", timedelta(days=3)),
    ("нагадай мені через 2 місяці", relativedelta(months=2)),
    ("це сталося 3 дні тому", timedelta(days=-3)),
])
def test_sentence_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("word,off", [("сьогодні", 0), ("завтра", 1),
                                      ("вчора", -1), ("післязавтра", 2),
                                      ("позавчора", -2)])
def test_named_day(word, off):
    assert start(word) == ad((ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0))


_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("наступний понеділок", _MID + timedelta(days=6)),
    ("наступна п'ятниця", _MID + timedelta(days=3)),
    ("минула п'ятниця", _MID - timedelta(days=4)),
    ("минулий вівторок", _MID - timedelta(days=7)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


# deposited NON_MATCHES: marker or number alone is not an offset
def test_offset_needs_marker():
    assert parse("через 2") is None
    assert parse("2 тому") is None
    nomatch("три дні")
