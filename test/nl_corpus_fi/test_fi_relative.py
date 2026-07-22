"""Finnish relative offsets in BOTH directions: the genitive-cased "N UNIT
kuluttua" (in / future) and "N UNIT sitten" (ago / past), named days
(tänään/huomenna/eilen/ylihuomenna/toissapäivänä) and weekday references
(ensi/viime + the essive weekday, "ensi maanantaina").  The offset numeral
uses the genitive in the future slot ("kahden viikon"); oracles are
independent date arithmetic, never the engine's own output.
"""
import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, start_end, nomatch

UNIT = {
    "päivä": relativedelta(days=1), "päivää": relativedelta(days=1),
    "päivän": relativedelta(days=1),
    "viikko": relativedelta(weeks=1), "viikkoa": relativedelta(weeks=1),
    "viikon": relativedelta(weeks=1),
    "kuukausi": relativedelta(months=1), "kuukautta": relativedelta(months=1),
    "kuukauden": relativedelta(months=1),
    "vuosi": relativedelta(years=1), "vuotta": relativedelta(years=1),
    "vuoden": relativedelta(years=1),
    "tunti": relativedelta(hours=1), "tuntia": relativedelta(hours=1),
    "tunnin": relativedelta(hours=1),
    "minuutti": relativedelta(minutes=1), "minuuttia": relativedelta(minutes=1),
    "minuutin": relativedelta(minutes=1),
}


def past(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR - n * d), ad(ANCHOR - (n - 1) * d)


def future(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR + n * d), ad(ANCHOR + (n + 1) * d)


# -- future: "N UNIT-genitive kuluttua" -----------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("kolmen päivän kuluttua", 3, "päivän"),
    ("viikon kuluttua", 1, "viikon"),
    ("kahden viikon kuluttua", 2, "viikon"),
    ("kolmen viikon kuluttua", 3, "viikon"),
    ("viiden kuukauden kuluttua", 5, "kuukauden"),
    ("kymmenen vuoden kuluttua", 10, "vuoden"),
    ("kahden tunnin kuluttua", 2, "tunnin"),
    ("kolmen päivän päästä", 3, "päivän"),
    ("viikon päästä", 1, "viikon"),
])
def test_future(text, n, unit):
    assert start_end(text) == future(n, unit)


# -- past: "N UNIT-partitive sitten" --------------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("kolme päivää sitten", 3, "päivää"),
    ("kaksi viikkoa sitten", 2, "viikkoa"),
    ("viisi kuukautta sitten", 5, "kuukautta"),
    ("kymmenen vuotta sitten", 10, "vuotta"),
    ("kolme tuntia sitten", 3, "tuntia"),
    ("seitsemän päivää sitten", 7, "päivää"),
    ("30 minuuttia sitten", 30, "minuuttia"),
])
def test_past(text, n, unit):
    assert start_end(text) == past(n, unit)


# -- named days -----------------------------------------------------------

@pytest.mark.parametrize("text,offset", [
    ("tänään", 0), ("huomenna", 1), ("eilen", -1),
    ("ylihuomenna", 2), ("toissapäivänä", -2),
])
def test_named_days(text, offset):
    from datetime import timedelta
    base = (ANCHOR + timedelta(days=offset)).replace(hour=0, minute=0)
    assert start(text) == ad(base)


# -- weekday references (anchor 2017-06-27 is a Tuesday) ------------------

@pytest.mark.parametrize("text,y,mo,d", [
    ("ensi maanantaina", 2017, 7, 3),
    ("ensi tiistaina", 2017, 7, 4),
    ("ensi perjantaina", 2017, 6, 30),
    ("viime perjantaina", 2017, 6, 23),
    ("viime maanantaina", 2017, 6, 26),
    ("viime sunnuntaina", 2017, 6, 25),
])
def test_weekday_ref(text, y, mo, d):
    from datetime import datetime
    assert start(text) == ad(datetime(y, mo, d))


def test_bare_number_no_unit_nomatch():
    nomatch("kaksikymmentäkolme")


def test_gibberish_nomatch():
    nomatch("syön omenoita joka aamu")
