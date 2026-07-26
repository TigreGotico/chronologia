"""Hungarian relative offsets in BOTH directions: the postposed "N UNIT
múlva" (in / future) and "N UNIT-instrumental ezelőtt" (ago / past), named
days (ma/holnap/tegnap/holnapután/tegnapelőtt) and weekday references
(jövő/múlt + the superessive weekday, "jövő hétfőn").  Oracles are
independent date arithmetic, never the engine's own output.
"""
import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, start_end, nomatch

UNIT = {
    "nap": relativedelta(days=1), "nappal": relativedelta(days=1),
    "hét": relativedelta(weeks=1), "héttel": relativedelta(weeks=1),
    "hónap": relativedelta(months=1), "hónappal": relativedelta(months=1),
    "év": relativedelta(years=1), "évvel": relativedelta(years=1),
    "óra": relativedelta(hours=1), "órával": relativedelta(hours=1),
    "perc": relativedelta(minutes=1), "perccel": relativedelta(minutes=1),
}


def past(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR - n * d), ad(ANCHOR - (n - 1) * d)


def future(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR + n * d), ad(ANCHOR + (n + 1) * d)


# -- future: "N UNIT múlva" -----------------------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("3 nap múlva", 3, "nap"),
    ("három nap múlva", 3, "nap"),
    ("2 hét múlva", 2, "hét"),
    ("két hét múlva", 2, "hét"),
    ("5 hónap múlva", 5, "hónap"),
    ("öt hónap múlva", 5, "hónap"),
    ("10 év múlva", 10, "év"),
    ("tíz év múlva", 10, "év"),
    ("3 óra múlva", 3, "óra"),
    ("15 perc múlva", 15, "perc"),
    ("negyven perc múlva", 40, "perc"),
    ("egy hét múlva", 1, "hét"),
])
def test_future(text, n, unit):
    assert start_end(text) == future(n, unit)


# -- past: "N UNIT-instrumental ezelőtt" ----------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("3 nappal ezelőtt", 3, "nappal"),
    ("három nappal ezelőtt", 3, "nappal"),
    ("2 héttel ezelőtt", 2, "héttel"),
    ("két héttel ezelőtt", 2, "héttel"),
    ("5 hónappal ezelőtt", 5, "hónappal"),
    ("10 évvel ezelőtt", 10, "évvel"),
    ("öt évvel ezelőtt", 5, "évvel"),
    ("30 perccel ezelőtt", 30, "perccel"),
    ("2 órával ezelőtt", 2, "órával"),
])
def test_past(text, n, unit):
    assert start_end(text) == past(n, unit)


# -- named days -----------------------------------------------------------

@pytest.mark.parametrize("text,offset", [
    ("ma", 0), ("holnap", 1), ("tegnap", -1),
    ("holnapután", 2), ("tegnapelőtt", -2),
])
def test_named_days(text, offset):
    from datetime import timedelta
    base = (ANCHOR + timedelta(days=offset)).replace(hour=0, minute=0)
    assert start(text) == ad(base)


# -- weekday references (anchor 2017-06-27 is a Tuesday) ------------------

@pytest.mark.parametrize("text,y,mo,d", [
    ("jövő hétfőn", 2017, 7, 3),
    ("jövő kedden", 2017, 7, 4),
    ("jövő pénteken", 2017, 6, 30),
    ("múlt pénteken", 2017, 6, 23),
    ("múlt hétfőn", 2017, 6, 26),
    ("előző vasárnap", 2017, 6, 25),
])
def test_weekday_ref(text, y, mo, d):
    from datetime import datetime
    assert start(text) == ad(datetime(y, mo, d))


def test_bare_number_no_unit_nomatch():
    nomatch("huszonhárom")


def test_gibberish_nomatch():
    # true gibberish with no temporal token (the former "minden reggel almát
    # eszem" now binds the daypart 'reggel' -- see test_hu_adversarial.py).
    nomatch("qwrt zxcv plmn")
