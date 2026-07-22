"""Holiday references in German (``holiday_ref``).

Anchor 2017-06-27.  Western computus (independent table): Easter 2016 = 27 Mar,
2017 = 16 Apr, 2018 = 1 Apr, 2020 = 12 Apr.  Bare rule = next occurrence on or
after the anchor.  Pentecost = Easter+49, Corpus Christi = Easter+60.  Every
expected date derived by hand.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("weihnachten", (2017, 12, 25)),
    ("heiligabend", (2017, 12, 24)),
    ("silvester", (2017, 12, 31)),
    ("neujahr", (2018, 1, 1)),
    ("dreikönigstag", (2018, 1, 6)),
    ("mariä himmelfahrt", (2017, 8, 15)),
    ("allerheiligen", (2017, 11, 1)),
    ("ostern", (2018, 4, 1)),
    ("karfreitag", (2018, 3, 30)),
    ("ostermontag", (2018, 4, 2)),
    ("christi himmelfahrt", (2018, 5, 10)),
    ("pfingsten", (2018, 5, 20)),
    ("fronleichnam", (2018, 5, 31)),
    ("karneval", (2018, 2, 13)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("wann ist weihnachten", (2017, 12, 25)),
    ("wann ist ostern", (2018, 4, 1)),
])
def test_when_is(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("nächste weihnachten", (2017, 12, 25)),
    ("letzte weihnachten", (2016, 12, 25)),
    ("letzte ostern", (2017, 4, 16)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("weihnachten 2020", (2020, 12, 25)),
    ("ostern 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


def test_confusable_still_binds_easter():
    r = parse("frohe ostern euch allen")
    assert r is not None and r[0].start == AstroDate(2018, 4, 1)


@pytest.mark.parametrize("text", [
    "der preis der eier ist gestiegen",
    "ein treffen über das budget",
])
def test_no_holiday_no_match(text):
    nomatch(text)


@pytest.mark.xfail(reason="holiday/name homograph out of scope")
def test_name_homograph_should_not_bind():
    nomatch("sie heißt ostern")


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
    ('zuckerfest', (2018, 6, 15)),
    ('ramadan', (2018, 5, 16)),
    ('islamisches neujahr', (2017, 9, 21)),
    ('rosch haschana', (2017, 9, 21)),
    ('jom kippur', (2017, 9, 30)),
    ('pessach', (2018, 3, 31)),
    ('chanukka', (2017, 12, 13)),
    ('chinesisches neujahr', (2018, 2, 16)),
    ('mondfest', (2017, 10, 4)),
    ('nouruz', (2018, 3, 21)),
    ('diwali', (2017, 10, 19)),
    ('vesakh', (2018, 5, 29)),
    ('halloween', (2017, 10, 31)),
    ('valentinstag', (2018, 2, 14)),
    ('muttertag', (2018, 5, 13)),
    ('vatertag', (2018, 5, 10)),
    ('opferfest', (2017, 9, 1)),
]


@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('diwali 2026', (2026, 11, 8)),
    ('chinesisches neujahr 2026', (2026, 2, 17)),
    ('pessach 2026', (2026, 4, 2)),
])
def test_explicit_year_expanded(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text", [
    'der reispreis stieg',
    'eine schüssel suppe',
    'ein arbeitstreffen',
])
def test_expanded_no_match(text):
    nomatch(text)
