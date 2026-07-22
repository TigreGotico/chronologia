"""Holiday references in Galician (``holiday_ref``).

Anchor 2017-06-27.  Western computus (independent table): Easter 2016 = 27 Mar,
2017 = 16 Apr, 2018 = 1 Apr, 2020 = 12 Apr.  Bare rule = next occurrence on or
after the anchor.  Carnival (Entroido) = Easter-47.  Every expected date derived
by hand.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("nadal", (2017, 12, 25)),
    ("día de nadal", (2017, 12, 25)),
    ("noiteboa", (2017, 12, 24)),
    ("aninovo", (2018, 1, 1)),
    ("día de reis", (2018, 1, 6)),
    ("asunción", (2017, 8, 15)),
    ("todos os santos", (2017, 11, 1)),
    ("pascua", (2018, 4, 1)),
    ("domingo de pascua", (2018, 4, 1)),
    ("venres santo", (2018, 3, 30)),
    ("luns de pascua", (2018, 4, 2)),
    ("ascensión", (2018, 5, 10)),
    ("entroido", (2018, 2, 13)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("cando é o nadal", (2017, 12, 25)),
    ("cando é a pascua", (2018, 4, 1)),
])
def test_when_is(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("próximo nadal", (2017, 12, 25)),
    ("último nadal", (2016, 12, 25)),
    ("última pascua", (2017, 4, 16)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("nadal 2020", (2020, 12, 25)),
    ("pascua 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


def test_confusable_still_binds_easter():
    r = parse("ovos de pascua")
    assert r is not None and r[0].start == AstroDate(2018, 4, 1)
    assert "ovos" in r[1]


@pytest.mark.parametrize("text", [
    "o prezo dos ovos subiu",
    "unha reunión sobre o orzamento",
])
def test_no_holiday_no_match(text):
    nomatch(text)


@pytest.mark.xfail(reason="holiday/surname homograph (Nadal) out of scope")
def test_name_homograph_should_not_bind():
    nomatch("o tenista nadal xogou")


# ==========================================================================
# EXPANDED SET -- non-Christian / non-Western well-known holidays.
# Anchor stays 2017-06-27 (Tuesday); bare = next occurrence on or after it.
# Movable non-Gregorian dates come from independent published tables,
# cross-checked against this engine's own tabulated calendars (Umm al-Qura,
# arithmetic Hebrew, tabulated Chinese, arithmetic Solar Hijri) and, where no
# closed form is modelled here (Diwali, Vesak), from the WELL_KNOWN decree
# tables. Mother's/Father's Day use this locale's jurisdiction default.
# ==========================================================================

_EXPANDED = [
    ('eid', (2018, 6, 15)),
    ('ramadán', (2018, 5, 16)),
    ('ano novo xudeu', (2017, 9, 21)),
    ('yom kippur', (2017, 9, 30)),
    ('pésaj', (2018, 3, 31)),
    ('janucá', (2017, 12, 13)),
    ('ano novo chinés', (2018, 2, 16)),
    ('festa do medio outono', (2017, 10, 4)),
    ('nowruz', (2018, 3, 21)),
    ('diwali', (2017, 10, 19)),
    ('vesak', (2018, 5, 29)),
    ('samaín', (2017, 10, 31)),
    ('san valentín', (2018, 2, 14)),
    ('día da nai', (2018, 5, 6)),
    ('día do pai', (2018, 3, 19)),
    ('acción de grazas', (2017, 11, 23)),
]


@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('diwali 2026', (2026, 11, 8)),
    ('ano novo chinés 2026', (2026, 2, 17)),
    ('pésaj 2026', (2026, 4, 2)),
])
def test_explicit_year_expanded(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text", [
    'o prezo do arroz subiu',
    'unha cunca de sopa',
    'unha reunión de traballo',
])
def test_expanded_no_match(text):
    nomatch(text)
