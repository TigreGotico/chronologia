"""Holiday references in Spanish (``holiday_ref``).

Anchor 2017-06-27.  Western computus (independent table): Easter 2016 = 27 Mar,
2017 = 16 Apr, 2018 = 1 Apr, 2020 = 12 Apr.  Bare rule = next occurrence on or
after the anchor.  Every expected date derived by hand.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("navidad", (2017, 12, 25)),
    ("día de navidad", (2017, 12, 25)),
    ("nochebuena", (2017, 12, 24)),
    ("año nuevo", (2018, 1, 1)),
    ("día de reyes", (2018, 1, 6)),
    ("reyes", (2018, 1, 6)),
    ("asunción", (2017, 8, 15)),
    ("todos los santos", (2017, 11, 1)),
    ("pascua", (2018, 4, 1)),
    ("viernes santo", (2018, 3, 30)),
    ("ascensión", (2018, 5, 10)),
    ("corpus christi", (2018, 5, 31)),
    ("carnaval", (2018, 2, 13)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("cuándo es navidad", (2017, 12, 25)),
    ("cuándo es la pascua", (2018, 4, 1)),
])
def test_when_is(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("próxima navidad", (2017, 12, 25)),
    ("última navidad", (2016, 12, 25)),
    ("última pascua", (2017, 4, 16)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("navidad 2020", (2020, 12, 25)),
    ("pascua 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


def test_confusable_still_binds_easter():
    r = parse("huevos de pascua")
    assert r is not None and r[0].start == AstroDate(2018, 4, 1)
    assert "huevos" in r[1]


@pytest.mark.parametrize("text", [
    "el precio de los huevos subió",
    "una reunión sobre el presupuesto",
])
def test_no_holiday_no_match(text):
    nomatch(text)


@pytest.mark.xfail(reason="holiday/person homograph out of scope")
def test_person_homograph_should_not_bind():
    nomatch("conocí a una chica llamada pascua")
