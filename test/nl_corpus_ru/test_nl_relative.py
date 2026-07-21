"""Russian relative offsets in both directions.

"через N <unit>" shifts forward (prefix marker), "N <unit> назад" shifts back
(suffix marker); the sign is the marker's declared direction, so a past
phrase can never leak forward.  Expected values are independent Python date
arithmetic against the Tuesday 2017-06-27 13:04 anchor.  Unit nouns carry the
case the count governs (genitive singular after 2-4, genitive plural after
5+).  Values mirror the deposited ru period-offset golds.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, parse, nomatch


# -- days ----------------------------------------------------------------

@pytest.mark.parametrize("n,form", [(1, "день"), (2, "дня"), (3, "дня"),
                                    (5, "дней"), (10, "дней"), (21, "день")])
def test_days_future(n, form):
    assert start(f"через {n} {form}") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "день"), (2, "дня"), (3, "дня"),
                                    (5, "дней"), (10, "дней")])
def test_days_past(n, form):
    assert start(f"{n} {form} назад") == ad(ANCHOR - timedelta(days=n))


# -- weeks ---------------------------------------------------------------

@pytest.mark.parametrize("n,form", [(1, "неделю"), (2, "недели"), (3, "недели"),
                                    (5, "недель")])
def test_weeks_future(n, form):
    assert start(f"через {n} {form}") == ad(ANCHOR + timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(2, "недели"), (3, "недель"), (5, "недель")])
def test_weeks_past(n, form):
    assert start(f"{n} {form} назад") == ad(ANCHOR - timedelta(weeks=n))


# -- months --------------------------------------------------------------

@pytest.mark.parametrize("n,form", [(1, "месяц"), (2, "месяца"), (3, "месяца"),
                                    (5, "месяцев"), (8, "месяцев")])
def test_months_future(n, form):
    assert start(f"через {n} {form}") == ad(ANCHOR + relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(2, "месяца"), (5, "месяцев"), (3, "месяца")])
def test_months_past(n, form):
    assert start(f"{n} {form} назад") == ad(ANCHOR - relativedelta(months=n))


# -- years ---------------------------------------------------------------

@pytest.mark.parametrize("n,form", [(1, "год"), (2, "года"), (3, "года"),
                                    (5, "лет"), (10, "лет"), (20, "лет")])
def test_years_future(n, form):
    assert start(f"через {n} {form}") == ad(ANCHOR + relativedelta(years=n))


@pytest.mark.parametrize("n,form", [(2, "года"), (5, "лет"), (10, "лет")])
def test_years_past(n, form):
    assert start(f"{n} {form} назад") == ad(ANCHOR - relativedelta(years=n))


# -- hours and minutes ---------------------------------------------------

@pytest.mark.parametrize("n,form", [(1, "час"), (2, "часа"), (3, "часа"),
                                    (5, "часов")])
def test_hours_future(n, form):
    assert start(f"через {n} {form}") == ad(ANCHOR + timedelta(hours=n))


@pytest.mark.parametrize("n", [5, 10, 15, 30, 45])
def test_minutes_future(n):
    assert start(f"через {n} минут") == ad(ANCHOR + timedelta(minutes=n))


# -- spelled numbers fold like digits ------------------------------------

@pytest.mark.parametrize("phrase,delta", [
    ("через пять дней", timedelta(days=5)),
    ("через три недели", timedelta(weeks=3)),
    ("через десять минут", timedelta(minutes=10)),
    ("через двадцать минут", timedelta(minutes=20)),
])
def test_spelled_offset(phrase, delta):
    assert start(phrase) == ad(ANCHOR + delta)


# -- natural sentences (marker embedded in a request) --------------------

@pytest.mark.parametrize("text,delta", [
    ("встретимся через 3 дня", timedelta(days=3)),
    ("напомни мне через 2 месяца", relativedelta(months=2)),
    ("это случилось 3 дня назад", timedelta(days=-3)),
])
def test_sentence_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


# -- named days ----------------------------------------------------------

@pytest.mark.parametrize("word,off", [("сегодня", 0), ("завтра", 1),
                                      ("вчера", -1), ("послезавтра", 2),
                                      ("позавчера", -2)])
def test_named_day(word, off):
    assert start(word) == ad((ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0))


# -- weekday reference ---------------------------------------------------

_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("следующий понедельник", _MID + timedelta(days=6)),
    ("следующая пятница", _MID + timedelta(days=3)),
    ("прошлая пятница", _MID - timedelta(days=4)),
    ("прошлый вторник", _MID - timedelta(days=7)),
    ("этот четверг", _MID + timedelta(days=2)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


# adversarial: an offset with no marker is not an offset
def test_offset_needs_marker():
    nomatch("три дня")
    nomatch("пять лет")
    assert parse("минут") is None
