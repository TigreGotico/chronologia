"""Holiday references in Dutch (``holiday_ref``).

Anchor 2017-06-27.  Western computus (independent table): Easter 2016 = 27 Mar,
2017 = 16 Apr, 2018 = 1 Apr, 2020 = 12 Apr.  Bare rule = next occurrence on or
after the anchor.  Pentecost (Pinksteren) = Easter+49.  Every expected date
derived by hand.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("kerstmis", (2017, 12, 25)),
    ("kerst", (2017, 12, 25)),
    ("kerstavond", (2017, 12, 24)),
    ("nieuwjaar", (2018, 1, 1)),
    ("driekoningen", (2018, 1, 6)),
    ("allerheiligen", (2017, 11, 1)),
    ("pasen", (2018, 4, 1)),
    ("goede vrijdag", (2018, 3, 30)),
    ("paasmaandag", (2018, 4, 2)),
    ("hemelvaartsdag", (2018, 5, 10)),
    ("pinksteren", (2018, 5, 20)),
    ("carnaval", (2018, 2, 13)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("wanneer is kerstmis", (2017, 12, 25)),
    ("wanneer is pasen", (2018, 4, 1)),
])
def test_when_is(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("volgende kerstmis", (2017, 12, 25)),
    ("vorige kerstmis", (2016, 12, 25)),
    ("vorige pasen", (2017, 4, 16)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("kerstmis 2020", (2020, 12, 25)),
    ("pasen 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


def test_confusable_still_binds_easter():
    r = parse("vrolijk pasen allemaal")
    assert r is not None and r[0].start == AstroDate(2018, 4, 1)


@pytest.mark.parametrize("text", [
    "de prijs van eieren is gestegen",
    "een vergadering over het budget",
])
def test_no_holiday_no_match(text):
    nomatch(text)


@pytest.mark.xfail(reason="holiday/surname homograph out of scope")
def test_name_homograph_should_not_bind():
    nomatch("de familie kerst woont hier")
