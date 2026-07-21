"""Slovak relative offsets in both directions.

Future markers za / o / cez shift forward; "pred" shifts back.  The sign is
the marker's declared direction.  Unit nouns carry the case the count and
preposition govern (nominative/accusative after za, instrumental after pred:
"pred 2 týždňami", "pred 5 rokmi").  Expected values are independent Python
date arithmetic against the Tuesday 2017-06-27 13:04 anchor.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, parse, nomatch


@pytest.mark.parametrize("n,form", [(1, "deň"), (2, "dni"), (3, "dni"),
                                    (5, "dní"), (10, "dní")])
def test_days_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "dňom"), (2, "dňami"), (5, "dňami"),
                                    (2, "dňoch")])
def test_days_past(n, form):
    assert start(f"pred {n} {form}") == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "týždeň"), (2, "týždne"), (3, "týždne"),
                                    (5, "týždňov")])
def test_weeks_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + timedelta(weeks=n))


@pytest.mark.parametrize("n", [2, 3, 5])
def test_weeks_past(n):
    assert start(f"pred {n} týždňami") == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(1, "mesiac"), (2, "mesiace"),
                                    (3, "mesiace"), (5, "mesiacov"),
                                    (8, "mesiacov")])
def test_months_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + relativedelta(months=n))


@pytest.mark.parametrize("n", [2, 5, 3])
def test_months_past(n):
    assert start(f"pred {n} mesiacmi") == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(1, "rok"), (2, "roky"), (3, "roky"),
                                    (5, "rokov"), (10, "rokov")])
def test_years_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + relativedelta(years=n))


@pytest.mark.parametrize("n", [2, 5, 10])
def test_years_past_rokmi(n):
    assert start(f"pred {n} rokmi") == ad(ANCHOR - relativedelta(years=n))


# -- future markers o / cez, hours and minutes ---------------------------

@pytest.mark.parametrize("n", [5, 10, 25, 45])
def test_minutes_o(n):
    assert start(f"o {n} minút") == ad(ANCHOR + timedelta(minutes=n))


@pytest.mark.parametrize("n,form", [(1, "hodinu"), (2, "hodiny"), (3, "hodiny"),
                                    (5, "hodín")])
def test_hours_cez(n, form):
    assert start(f"cez {n} {form}") == ad(ANCHOR + timedelta(hours=n))


# -- spelled numbers fold like digits ------------------------------------

@pytest.mark.parametrize("phrase,delta", [
    ("za päť dní", timedelta(days=5)),
    ("o desať minút", timedelta(minutes=10)),
    ("za dvadsaťpäť minút", timedelta(minutes=25)),
    ("cez tri hodiny", timedelta(hours=3)),
])
def test_spelled_offset(phrase, delta):
    assert start(phrase) == ad(ANCHOR + delta)


# -- named days ----------------------------------------------------------

@pytest.mark.parametrize("word,off", [("dnes", 0), ("zajtra", 1), ("včera", -1),
                                      ("pozajtra", 2), ("predvčerom", -2)])
def test_named_day(word, off):
    assert start(word) == ad((ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0))


# -- weekday reference ---------------------------------------------------

_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("budúci pondelok", _MID + timedelta(days=6)),
    ("budúcu stredu", _MID + timedelta(days=1)),
    ("budúci piatok", _MID + timedelta(days=3)),
    ("minulý piatok", _MID - timedelta(days=4)),
    ("minulý utorok", _MID - timedelta(days=7)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


def test_offset_needs_marker():
    nomatch("päť dní")
    nomatch("dva týždne")
    assert parse("minút") is None
