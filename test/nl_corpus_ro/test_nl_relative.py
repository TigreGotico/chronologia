"""Romanian relative phrases: "peste N unitati", "acum N unitati" (prefix
past marker), viitor/trecut weekdays, named days, indefinite one."""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, nomatch, span


_NW = {2: "două", 3: "trei", 4: "patru", 5: "cinci", 6: "șase",
       7: "șapte", 8: "opt", 9: "nouă", 10: "zece", 12: "doisprezece"}


def _day_cases():
    out = []
    for n in (2, 3, 4, 5, 6, 7, 8, 10):
        out.append((f"acum {n} zile", ANCHOR - timedelta(days=n)))
        out.append((f"peste {n} zile", ANCHOR + timedelta(days=n)))
        out.append((f"acum {_NW[n]} zile", ANCHOR - timedelta(days=n)))
        out.append((f"peste {_NW[n]} zile", ANCHOR + timedelta(days=n)))
    return out


def _week_cases():
    out = []
    for n in (2, 3, 4, 6):
        out.append((f"acum {n} săptămâni", ANCHOR - timedelta(weeks=n)))
        out.append((f"peste {n} săptămâni", ANCHOR + timedelta(weeks=n)))
        out.append((f"peste {_NW[n]} săptămâni", ANCHOR + timedelta(weeks=n)))
    return out


def _month_cases():
    return [(f"acum {n} luni", ANCHOR - relativedelta(months=n)) for n in (2, 3, 6)] + \
           [(f"peste {n} luni", ANCHOR + relativedelta(months=n)) for n in (2, 3, 6)]


def _year_cases():
    return [(f"acum {n} ani", ANCHOR - relativedelta(years=n)) for n in (2, 3, 5, 10)] + \
           [(f"peste {n} ani", ANCHOR + relativedelta(years=n)) for n in (2, 3, 5, 10)]


@pytest.mark.parametrize("text,expected",
                         _day_cases() + _week_cases()
                         + _month_cases() + _year_cases())
def test_relative_offset(text, expected):
    assert start(text) == ad(expected)


@pytest.mark.parametrize("text,delta", [
    ("peste 3 ore", timedelta(hours=3)),
    ("peste 10 minute", timedelta(minutes=10)),
    ("acum 3 ore", timedelta(hours=-3)),
    ("acum 30 minute", timedelta(minutes=-30)),
])
def test_subday_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,expected", [
    ("azi", ANCHOR.replace(hour=0, minute=0)),
    ("mâine", (ANCHOR + timedelta(days=1)).replace(hour=0, minute=0)),
    ("ieri", (ANCHOR - timedelta(days=1)).replace(hour=0, minute=0)),
    ("poimâine", (ANCHOR + timedelta(days=2)).replace(hour=0, minute=0)),
    ("alaltăieri", (ANCHOR - timedelta(days=2)).replace(hour=0, minute=0)),
])
def test_named_day(text, expected):
    assert start(text) == ad(expected)


_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("luni viitoare", _MID + timedelta(days=6)),
    ("miercuri viitoare", _MID + timedelta(days=1)),
    ("vineri viitoare", _MID + timedelta(days=3)),
    ("duminică viitoare", _MID + timedelta(days=5)),
    ("luni trecută", _MID - timedelta(days=1)),
    ("sâmbătă trecută", _MID - timedelta(days=3)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


def test_widths():
    assert span("mâine").width == timedelta(days=1)
    assert span("peste 2 săptămâni").width == timedelta(weeks=1)


@pytest.mark.parametrize("text,delta", [
    ("peste o săptămână", timedelta(weeks=1)),
    ("acum un an", relativedelta(years=-1)),
])
def test_indefinite_one(text, delta):
    assert start(text) == ad(ANCHOR + delta)


def test_symmetry():
    assert (start("peste 2 săptămâni") - start("acum 2 săptămâni")) == timedelta(days=28)


def test_gibberish():
    nomatch("")
    nomatch("qwerty azerty")
