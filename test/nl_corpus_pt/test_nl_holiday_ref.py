"""Holiday references in Portuguese (``holiday_ref``).

Anchor 2017-06-27 (Tuesday).  Western computus (independent table):
Easter 2016 = 27 Mar, 2017 = 16 Apr, 2018 = 1 Apr, 2020 = 12 Apr.  Bare rule =
next occurrence on or after the anchor.  Every expected date derived by hand.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

_BARE = [
    ("natal", (2017, 12, 25)),
    ("dia de natal", (2017, 12, 25)),
    ("véspera de natal", (2017, 12, 24)),
    ("ano novo", (2018, 1, 1)),
    ("dia de reis", (2018, 1, 6)),
    ("assunção", (2017, 8, 15)),
    ("dia de todos os santos", (2017, 11, 1)),
    ("páscoa", (2018, 4, 1)),
    ("domingo de páscoa", (2018, 4, 1)),
    ("sexta-feira santa", (2018, 3, 30)),
    ("ascensão", (2018, 5, 10)),
    ("corpo de deus", (2018, 5, 31)),
    ("carnaval", (2018, 2, 13)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("quando é o natal", (2017, 12, 25)),
    ("quando é a páscoa", (2018, 4, 1)),
])
def test_when_is(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("próximo natal", (2017, 12, 25)),
    ("último natal", (2016, 12, 25)),
    ("última páscoa", (2017, 4, 16)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("natal 2020", (2020, 12, 25)),
    ("páscoa 2020", (2020, 4, 12)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


def test_confusable_still_binds_easter():
    r = parse("ovos da páscoa")
    assert r is not None and r[0].start == AstroDate(2018, 4, 1)
    assert "ovos" in r[1]


@pytest.mark.parametrize("text", [
    "o preço dos ovos subiu",
    "uma reunião sobre o orçamento",
])
def test_no_holiday_no_match(text):
    nomatch(text)


@pytest.mark.xfail(reason="holiday/place homograph (Natal, Brazil) out of scope")
def test_place_homograph_should_not_bind():
    nomatch("vou para natal no brasil")


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
    ('eid al-fitr', (2018, 6, 15)),
    ('ramadão', (2018, 5, 16)),
    ('ano novo islâmico', (2017, 9, 21)),
    ('rosh hashaná', (2017, 9, 21)),
    ('yom kippur', (2017, 9, 30)),
    ('pessach', (2018, 3, 31)),
    ('chanucá', (2017, 12, 13)),
    ('ano novo chinês', (2018, 2, 16)),
    ('festival do meio outono', (2017, 10, 4)),
    ('nowruz', (2018, 3, 21)),
    ('diwali', (2017, 10, 19)),
    ('vesak', (2018, 5, 29)),
    ('dia das bruxas', (2017, 10, 31)),
    ('dia dos namorados', (2018, 2, 14)),
    ('dia da mãe', (2018, 5, 6)),
    ('dia do pai', (2018, 3, 19)),
    ('ação de graças', (2017, 11, 23)),
]


@pytest.mark.parametrize("text,ymd", _EXPANDED)
def test_bare_expanded(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ('diwali 2026', (2026, 11, 8)),
    ('ano novo chinês 2026', (2026, 2, 17)),
    ('pessach 2026', (2026, 4, 2)),
])
def test_explicit_year_expanded(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text", [
    'o preço do arroz subiu',
    'uma tigela de sopa',
    'uma reunião de trabalho',
])
def test_expanded_no_match(text):
    nomatch(text)
