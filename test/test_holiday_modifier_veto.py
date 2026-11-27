"""A holiday name reads as a date only with a time cue next to it.

"the christmas spirit" and "chanson de noël" name no date; "for christmas",
"pour noël" and "am Ostersonntag" do.  A year scope in the same sentence
selects that year's holiday ("quest'anno a natale").

The anchor is Tuesday 2017-06-27.  Christmas 2017 (25 December) and New
Year's Eve 2017 are still ahead of it.  Western Easter 2018 is 1 April, by
the anonymous Gregorian computus below, which does not call the engine.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def gregorian_easter(year):
    """Anonymous Gregorian algorithm (Meeus, Astronomical Algorithms, ch. 8)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)


EASTER = gregorian_easter(2018)
CHRISTMAS = date(2017, 12, 25)


def day(text, lang):
    got = extract_timespan(text, lang, ANCHOR)
    if got is None:
        return None
    s = got.span.start
    return date(s.year, s.month, s.day)


def test_computus_oracle():
    assert EASTER == date(2018, 4, 1)


@pytest.mark.parametrize("lang,text", [
    ("en", "My grandmother loves the Christmas spirit in her old kitchen."),
    ("fr", "Elle chante une chanson de Noël avec sa grand-mère au salon."),
    ("pt", "Os ovos de Páscoa da avó são os melhores do mundo inteiro."),
    ("it", "Mia nonna dice che lo spirito del Natale si sente nei biscotti."),
])
def test_holiday_modifier_names_no_date(lang, text):
    assert day(text, lang) is None


@pytest.mark.parametrize("lang,text,want", [
    ("en", "We will visit grandma for Christmas with the whole family.",
     CHRISTMAS),
    ("fr", "Pour Noël nous irons chez ma grand-mère à la montagne.",
     CHRISTMAS),
    ("nl", "Met Pasen gaan we met de hele familie naar oma.", EASTER),
    ("de", "Zu Weihnachten fahren wir mit der ganzen Familie heim.",
     CHRISTMAS),
    ("de", "Am Ostersonntag suchen wir im Garten bunte Eier.", EASTER),
])
def test_holiday_with_a_time_cue_is_a_date(lang, text, want):
    assert day(text, lang) == want


@pytest.mark.parametrize("lang,text,want", [
    ("it", "Quest'anno a Natale andiamo tutti dalla nonna.", CHRISTMAS),
    ("pt", "Este ano, para a passagem de ano, queremos alugar uma casa.",
     date(2017, 12, 31)),
])
def test_year_scope_selects_the_holiday(lang, text, want):
    assert day(text, lang) == want


def test_consoada_is_christmas_eve():
    assert day("Na próxima Consoada vamos todos jantar a casa da avó.",
               "pt") == date(2017, 12, 24)


@pytest.mark.parametrize("lang,text", [
    ("sk", "Na budúcu Veľkonočnú nedeľu chceme ísť s rodinou na omšu."),
    ("cs", "Na Velikonoční neděli pojedeme s celou rodinou k babičce."),
    ("eu", "Datorren Pazko Igandean familia osoa amonaren etxean bilduko gara."),
    ("sl", "Na velikonočno nedeljo gremo z bratom k teti na Dolenjsko."),
    ("id", "Kami sekeluarga akan ke gereja pada Minggu Paskah nanti."),
    ("ms", "Kami sekeluarga akan ke gereja pada Ahad Paskah nanti."),
])
def test_inflected_easter_sunday_is_easter_not_a_sunday(lang, text):
    assert day(text, lang) == EASTER


@pytest.mark.xfail(raises=AssertionError, strict=True,
                   reason="TigreGotico/chronologia#1486: no hi holiday names")
def test_hindi_christmas_has_no_data():
    assert day("इस बार क्रिसमस पर हम दादी के घर जाएँगे।", "hi") == CHRISTMAS


@pytest.mark.xfail(raises=AssertionError, strict=True,
                   reason="TigreGotico/chronologia#1487: no ast Easter row")
def test_easter_sunday_without_data_is_a_sunday():
    assert day("Pal Domingu de Pascua tengo pensao xuntar la familia.",
               "ast") in (EASTER, None)
