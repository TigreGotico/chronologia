"""Holiday references in Italian (``holiday_ref``).

Anchor 2017-06-27.  Western computus (independent table): Easter 2016 = 27 Mar,
2017 = 16 Apr, 2018 = 1 Apr, 2020 = 12 Apr.  Bare rule = next occurrence on or
after the anchor.  Pentecost = Easter+49, Corpus Domini = Easter+60.  Every
expected date derived by hand.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("natale", (2017, 12, 25)),
    ("giorno di natale", (2017, 12, 25)),
    ("vigilia di natale", (2017, 12, 24)),
    ("capodanno", (2018, 1, 1)),
    ("befana", (2018, 1, 6)),
    ("ferragosto", (2017, 8, 15)),
    ("ognissanti", (2017, 11, 1)),
    ("pasqua", (2018, 4, 1)),
    ("venerdì santo", (2018, 3, 30)),
    ("pasquetta", (2018, 4, 2)),
    ("ascensione", (2018, 5, 10)),
    ("pentecoste", (2018, 5, 20)),
    ("corpus domini", (2018, 5, 31)),
    ("carnevale", (2018, 2, 13)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("quando è natale", (2017, 12, 25)),
    ("quando è pasqua", (2018, 4, 1)),
])
def test_when_is(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("prossimo natale", (2017, 12, 25)),
    ("scorso natale", (2016, 12, 25)),
    ("scorsa pasqua", (2017, 4, 16)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("natale 2020", (2020, 12, 25)),
    ("pasqua 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


def test_confusable_still_binds_easter():
    r = parse("le uova di pasqua")
    assert r is not None and r[0].start == AstroDate(2018, 4, 1)


@pytest.mark.parametrize("text", [
    "il prezzo delle uova è aumentato",
    "una riunione sul bilancio",
])
def test_no_holiday_no_match(text):
    nomatch(text)


@pytest.mark.xfail(reason="holiday/first-name homograph (Natale) out of scope")
def test_name_homograph_should_not_bind():
    nomatch("un uomo di nome natale")
