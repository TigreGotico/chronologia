"""Estonian relative offsets in BOTH directions: the genitive-cased "N UNIT
pärast" (in / future) and "N UNIT tagasi" (ago / past), named days
(täna/homme/eile/ülehomme/üleeile) and weekday references (järgmine/eelmine
+ the adessive weekday, "järgmisel esmaspäeval").  The future-offset numeral
uses the genitive ("kahe nädala"); oracles are independent date arithmetic.
"""
import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, start_end, nomatch

UNIT = {
    "päev": relativedelta(days=1), "päeva": relativedelta(days=1),
    "nädal": relativedelta(weeks=1), "nädala": relativedelta(weeks=1),
    "nädalat": relativedelta(weeks=1),
    "kuu": relativedelta(months=1), "kuud": relativedelta(months=1),
    "aasta": relativedelta(years=1), "aastat": relativedelta(years=1),
    "tund": relativedelta(hours=1), "tunni": relativedelta(hours=1),
    "tundi": relativedelta(hours=1),
    "minut": relativedelta(minutes=1), "minutit": relativedelta(minutes=1),
}


def past(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR - n * d), ad(ANCHOR - (n - 1) * d)


def future(n, unit):
    d = UNIT[unit]
    return ad(ANCHOR + n * d), ad(ANCHOR + (n + 1) * d)


# -- future: "N UNIT-genitive pärast" -------------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("kolme päeva pärast", 3, "päeva"),
    ("nädala pärast", 1, "nädala"),
    ("kahe nädala pärast", 2, "nädala"),
    ("kolme nädala pärast", 3, "nädala"),
    ("viie kuu pärast", 5, "kuu"),
    ("kümne aasta pärast", 10, "aasta"),
    ("kahe tunni pärast", 2, "tunni"),
    ("kolme päeva järel", 3, "päeva"),
])
def test_future(text, n, unit):
    assert start_end(text) == future(n, unit)


# -- past: "N UNIT tagasi" ------------------------------------------------

@pytest.mark.parametrize("text,n,unit", [
    ("kolm päeva tagasi", 3, "päeva"),
    ("kaks nädalat tagasi", 2, "nädalat"),
    ("viis kuud tagasi", 5, "kuud"),
    ("kümme aastat tagasi", 10, "aastat"),
    ("kolm tundi tagasi", 3, "tundi"),
    ("seitse päeva tagasi", 7, "päeva"),
    ("30 minutit tagasi", 30, "minutit"),
])
def test_past(text, n, unit):
    assert start_end(text) == past(n, unit)


# -- named days -----------------------------------------------------------

@pytest.mark.parametrize("text,offset", [
    ("täna", 0), ("homme", 1), ("eile", -1),
    ("ülehomme", 2), ("üleeile", -2),
])
def test_named_days(text, offset):
    from datetime import timedelta
    base = (ANCHOR + timedelta(days=offset)).replace(hour=0, minute=0)
    assert start(text) == ad(base)


# -- weekday references (anchor 2017-06-27 is a Tuesday) ------------------

@pytest.mark.parametrize("text,y,mo,d", [
    ("järgmisel esmaspäeval", 2017, 7, 3),
    ("järgmisel teisipäeval", 2017, 7, 4),
    ("järgmisel reedel", 2017, 6, 30),
    ("eelmisel reedel", 2017, 6, 23),
    ("eelmisel esmaspäeval", 2017, 6, 26),
    ("eelmisel pühapäeval", 2017, 6, 25),
])
def test_weekday_ref(text, y, mo, d):
    from datetime import datetime
    assert start(text) == ad(datetime(y, mo, d))


def test_bare_number_no_unit_nomatch():
    nomatch("kakskümmend kolm")


def test_gibberish_nomatch():
    nomatch("söön iga hommik õuna")
