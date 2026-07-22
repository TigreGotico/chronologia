"""Holiday references in French (``holiday_ref``).

Anchor 2017-06-27.  Western computus (independent table): Easter 2016 = 27 Mar,
2017 = 16 Apr, 2018 = 1 Apr, 2020 = 12 Apr.  Bare rule = next occurrence on or
after the anchor.  Good Friday = Easter-2, Pentecost = Easter+49, Corpus Christi
(Fête-Dieu) = Easter+60.  Every expected date derived by hand.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("noël", (2017, 12, 25)),
    ("jour de noël", (2017, 12, 25)),
    ("nouvel an", (2018, 1, 1)),
    ("épiphanie", (2018, 1, 6)),
    ("assomption", (2017, 8, 15)),
    ("toussaint", (2017, 11, 1)),
    ("pâques", (2018, 4, 1)),
    ("vendredi saint", (2018, 3, 30)),
    ("lundi de pâques", (2018, 4, 2)),
    ("ascension", (2018, 5, 10)),
    ("pentecôte", (2018, 5, 20)),
    ("fête-dieu", (2018, 5, 31)),
    ("carnaval", (2018, 2, 13)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("quand est noël", (2017, 12, 25)),
    ("quand est pâques", (2018, 4, 1)),
])
def test_when_is(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("prochain noël", (2017, 12, 25)),
    ("dernier noël", (2016, 12, 25)),
    ("dernier vendredi saint", (2017, 4, 14)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("noël 2020", (2020, 12, 25)),
    ("pâques 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


def test_confusable_still_binds_easter():
    r = parse("la chasse aux oeufs de pâques")
    assert r is not None and r[0].start == AstroDate(2018, 4, 1)


@pytest.mark.parametrize("text", [
    "le prix des oeufs a augmenté",
    "une réunion sur le budget",
])
def test_no_holiday_no_match(text):
    nomatch(text)


@pytest.mark.xfail(reason="holiday/first-name homograph (Noël) out of scope", strict=True)
def test_name_homograph_should_not_bind():
    nomatch("mon ami noël est venu")


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
    ('aïd', (2018, 6, 15)),
    ('nouvel an musulman', (2017, 9, 21)),
    ('roch hachana', (2017, 9, 21)),
    ('yom kippour', (2017, 9, 30)),
    ('pessah', (2018, 3, 31)),
    ('hanoucca', (2017, 12, 13)),
    ('nouvel an chinois', (2018, 2, 16)),
    ('fête de la mi-automne', (2017, 10, 4)),
    ('norouz', (2018, 3, 21)),
    ('diwali', (2017, 10, 19)),
    ('vesak', (2018, 5, 29)),
    ('halloween', (2017, 10, 31)),
    ('saint-valentin', (2018, 2, 14)),
    ('fête des mères', (2018, 5, 27)),
    ('fête des pères', (2018, 6, 17)),
    ('achoura', (2017, 9, 30)),
]


@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('diwali 2026', (2026, 11, 8)),
    ('nouvel an chinois 2026', (2026, 2, 17)),
    ('pessah 2026', (2026, 4, 2)),
])
def test_explicit_year_expanded(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text", [
    'le prix du riz a augmenté',
    'un bol de soupe',
    'une réunion de travail',
])
def test_expanded_no_match(text):
    nomatch(text)
