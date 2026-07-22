"""Holiday references in Catalan (``holiday_ref``).

Anchor 2017-06-27.  Western computus (independent table): Easter 2016 = 27 Mar,
2017 = 16 Apr, 2018 = 1 Apr, 2020 = 12 Apr.  Bare rule = next occurrence on or
after the anchor.  Corpus = Easter+60.  Every expected date derived by hand.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("nadal", (2017, 12, 25)),
    ("dia de nadal", (2017, 12, 25)),
    ("nit de nadal", (2017, 12, 24)),
    ("cap d'any", (2018, 1, 1)),
    ("reis", (2018, 1, 6)),
    ("tots sants", (2017, 11, 1)),
    ("pasqua", (2018, 4, 1)),
    ("diumenge de pasqua", (2018, 4, 1)),
    ("divendres sant", (2018, 3, 30)),
    ("dilluns de pasqua", (2018, 4, 2)),
    ("ascensió", (2018, 5, 10)),
    ("corpus", (2018, 5, 31)),
    ("carnaval", (2018, 2, 13)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("quan és nadal", (2017, 12, 25)),
    ("quan és pasqua", (2018, 4, 1)),
])
def test_when_is(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("pròxim nadal", (2017, 12, 25)),
    ("últim nadal", (2016, 12, 25)),
    ("última pasqua", (2017, 4, 16)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("nadal 2020", (2020, 12, 25)),
    ("pasqua 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


def test_confusable_still_binds_easter():
    r = parse("ous de pasqua")
    assert r is not None and r[0].start == AstroDate(2018, 4, 1)
    assert "ous" in r[1]


@pytest.mark.parametrize("text", [
    "el preu dels ous ha pujat",
    "una reunió sobre el pressupost",
])
def test_no_holiday_no_match(text):
    nomatch(text)


@pytest.mark.xfail(reason="holiday/surname homograph (Nadal) out of scope")
def test_name_homograph_should_not_bind():
    nomatch("el partit de nadal")
