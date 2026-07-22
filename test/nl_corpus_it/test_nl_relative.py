"""Italian relative phrases: "tra N unita", "N unita fa" (postfix past
marker), prossimo/scorso weekdays, named days, idiomatic compounds.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, nomatch, span


_NW = {1: "uno", 2: "due", 3: "tre", 4: "quattro", 5: "cinque", 6: "sei",
       7: "sette", 8: "otto", 9: "nove", 10: "dieci", 12: "dodici",
       20: "venti", 30: "trenta"}


def _day_cases():
    out = []
    for n in (2, 3, 5, 10, 20, 30):
        out.append((f"{n} giorni fa", ANCHOR - timedelta(days=n)))
        out.append((f"tra {n} giorni", ANCHOR + timedelta(days=n)))
        out.append((f"{_NW[n]} giorni fa", ANCHOR - timedelta(days=n)))
        out.append((f"tra {_NW[n]} giorni", ANCHOR + timedelta(days=n)))
    return out


def _week_cases():
    out = []
    for n in (2, 3, 4, 6):
        out.append((f"{n} settimane fa", ANCHOR - timedelta(weeks=n)))
        out.append((f"tra {n} settimane", ANCHOR + timedelta(weeks=n)))
        out.append((f"fra {_NW[n]} settimane", ANCHOR + timedelta(weeks=n)))
    return out


def _month_cases():
    out = []
    for n in (1, 2, 3, 6, 8, 12):
        out.append((f"{n} mesi fa", ANCHOR - relativedelta(months=n)))
        out.append((f"tra {n} mesi", ANCHOR + relativedelta(months=n)))
    return out


def _year_cases():
    out = []
    for n in (1, 2, 3, 5, 10, 20):
        out.append((f"{n} anni fa", ANCHOR - relativedelta(years=n)))
        out.append((f"tra {n} anni", ANCHOR + relativedelta(years=n)))
    return out


@pytest.mark.parametrize("text,expected",
                         _day_cases() + _week_cases()
                         + _month_cases() + _year_cases())
def test_relative_offset(text, expected):
    assert start(text) == ad(expected)


@pytest.mark.parametrize("text,delta", [
    ("tra 3 ore", timedelta(hours=3)),
    ("tra due ore", timedelta(hours=2)),
    ("tra 10 minuti", timedelta(minutes=10)),
    ("3 ore fa", timedelta(hours=-3)),
    ("30 minuti fa", timedelta(minutes=-30)),
])
def test_subday_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,expected", [
    ("oggi", ANCHOR.replace(hour=0, minute=0)),
    ("domani", (ANCHOR + timedelta(days=1)).replace(hour=0, minute=0)),
    ("ieri", (ANCHOR - timedelta(days=1)).replace(hour=0, minute=0)),
    ("dopodomani", (ANCHOR + timedelta(days=2)).replace(hour=0, minute=0)),
    ("altroieri", (ANCHOR - timedelta(days=2)).replace(hour=0, minute=0)),
])
def test_named_day(text, expected):
    assert start(text) == ad(expected)


_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("lunedì prossimo", _MID + timedelta(days=6)),
    ("martedì prossimo", _MID + timedelta(days=7)),
    ("mercoledì prossimo", _MID + timedelta(days=1)),
    ("venerdì prossimo", _MID + timedelta(days=3)),
    ("domenica prossima", _MID + timedelta(days=5)),
    ("lunedì scorso", _MID - timedelta(days=1)),
    ("martedì scorso", _MID - timedelta(days=7)),
    ("sabato scorso", _MID - timedelta(days=3)),
    ("domenica scorsa", _MID - timedelta(days=2)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


def test_widths():
    assert span("domani").width == timedelta(days=1)
    assert span("tra 3 giorni").width == timedelta(days=1)
    assert span("tra 2 settimane").width == timedelta(weeks=1)


@pytest.mark.parametrize("text,delta", [
    ("tra una settimana", timedelta(weeks=1)),
    ("una settimana fa", timedelta(weeks=-1)),
    ("tra un mese", relativedelta(months=1)),
    ("un anno fa", relativedelta(years=-1)),
])
def test_indefinite_one(text, delta):
    assert start(text) == ad(ANCHOR + delta)


def test_marker_without_offset():
    nomatch("azerty qwerty")
    nomatch("")


def test_symmetry():
    fut = start("tra 2 settimane")
    past = start("2 settimane fa")
    assert (fut - past) == timedelta(days=28)
