"""Basque relative offsets in BOTH directions: the preposed "duela N UNIT"
(ago / past) and the postposed "N UNIT barru" (in / future), named days
(gaur/bihar/atzo/etzi/herenegun) and weekday references (datorren/aurreko +
weekday).  Oracles are independent date arithmetic, never engine output.
"""
import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, start_end, nomatch

UNIT = {
    "egun": relativedelta(days=1),
    "aste": relativedelta(weeks=1),
    "hilabete": relativedelta(months=1),
    "urte": relativedelta(years=1),
    "ordu": relativedelta(hours=1),
    "minutu": relativedelta(minutes=1),
}


def past(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR - n * d), ad(ANCHOR - (n - 1) * d)


def future(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR + n * d), ad(ANCHOR + (n + 1) * d)


# -- past: "duela N UNIT" -------------------------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("duela 3 egun", 3, "egun"),
    ("duela hiru egun", 3, "egun"),
    ("duela bost egun", 5, "egun"),
    ("duela 2 aste", 2, "aste"),
    ("duela bi aste", 2, "aste"),
    ("duela 5 hilabete", 5, "hilabete"),
    ("duela 10 urte", 10, "urte"),
    ("duela hamar urte", 10, "urte"),
    ("duela 3 ordu", 3, "ordu"),
    ("duela 30 minutu", 30, "minutu"),
])
def test_past(text, n, unit):
    assert start_end(text) == past(n, unit)


# -- future: "N UNIT barru" -----------------------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("3 egun barru", 3, "egun"),
    ("hiru egun barru", 3, "egun"),
    ("2 aste barru", 2, "aste"),
    ("bi aste barru", 2, "aste"),
    ("5 hilabete barru", 5, "hilabete"),
    ("10 urte barru", 10, "urte"),
    ("hamar urte barru", 10, "urte"),
    ("3 ordu barru", 3, "ordu"),
    ("45 minutu barru", 45, "minutu"),
    ("aste bat barru", 1, "aste"),
])
def test_future(text, n, unit):
    assert start_end(text) == future(n, unit)


# -- named days -----------------------------------------------------------

@pytest.mark.parametrize("text,offset", [
    ("gaur", 0), ("bihar", 1), ("atzo", -1),
    ("etzi", 2), ("herenegun", -2),
])
def test_named_days(text, offset):
    from datetime import timedelta
    base = (ANCHOR + timedelta(days=offset)).replace(hour=0, minute=0)
    assert start(text) == ad(base)


# -- weekday references (anchor 2017-06-27 is a Tuesday) ------------------

@pytest.mark.parametrize("text,y,mo,d", [
    ("datorren astelehena", 2017, 7, 3),
    ("datorren asteartea", 2017, 7, 4),
    ("datorren ostirala", 2017, 6, 30),
    ("aurreko ostirala", 2017, 6, 23),
    ("aurreko astelehena", 2017, 6, 26),
    ("aurreko igandea", 2017, 6, 25),
])
def test_weekday_ref(text, y, mo, d):
    from datetime import datetime
    assert start(text) == ad(datetime(y, mo, d))


def test_bare_number_no_unit_nomatch():
    nomatch("hogeita hiru")


def test_gibberish_nomatch():
    nomatch("sagarrak jaten ditut goizero")
