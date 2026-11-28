"""Time cues that let a holiday name read as a date.

A relative word ("op", "ближайший", "φετινά"), a "this year" phrase in the
same clause ("i år", "idén", "letos", "امسال"), a word for day next to the
name ("pada hari", "Noel günü", "urteberri egunean", "karácsony első
napján") and a compound on the word for day ("húsvétvasárnap", "juledag")
each mark the name as a date.  A number, an offset word or another day word
in the clause makes the name the anchor of an offset, and the bare name is
not read.

The anchor is Tuesday 2017-06-27.  Western Easter 2018 is 1 April, by the
anonymous Gregorian computus below.  Orthodox Christmas is 25 December of
the Julian calendar, 13 days after the Gregorian date from 1900 to 2099.
"""
from datetime import date, datetime, timedelta

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
CHRISTMAS_EVE = date(2017, 12, 24)
CHRISTMAS = date(2017, 12, 25)
NEW_YEARS_EVE = date(2017, 12, 31)
NEW_YEAR = date(2018, 1, 1)
ORTHODOX_CHRISTMAS = CHRISTMAS + timedelta(days=13)


def day(text, lang):
    got = extract_timespan(text, lang, ANCHOR)
    if got is None:
        return None
    s = got.span.start
    return date(s.year, s.month, s.day)


def test_oracles():
    assert EASTER == date(2018, 4, 1)
    assert ORTHODOX_CHRISTMAS == date(2018, 1, 7)


@pytest.mark.parametrize("lang,text,want", [
    ("fy", "Op Âldjiersjûn wolle wy by pake en beppe oaljekoeken bakke.",
     NEW_YEARS_EVE),
    ("el", "Τα φετινά Χριστούγεννα σκοπεύουμε να μαζευτούμε στο χωριό.",
     CHRISTMAS),
    ("ru", "Бабушка решила, что на ближайшее Рождество мы поедем к ней.",
     ORTHODOX_CHRISTMAS),
    ("az", "Qarşıdakı Milad bayramında ailəmlə dağ kəndinə gedəcəm.",
     CHRISTMAS),
    ("sl", "Za božič bomo pri babici spekli orehovo potico.", CHRISTMAS),
    ("sl", "Za novo leto bomo z družino odšli v hribe.", NEW_YEAR),
    ("tr", "Noel günü bütün aileyi bizim evde toplamayı düşünüyorum.",
     CHRISTMAS),
])
def test_relative_word_or_preposition_is_a_cue(lang, text, want):
    assert day(text, lang) == want


@pytest.mark.parametrize("lang,text,want", [
    ("hu", "Idén szenteste a nagymamámnál gyűlik össze az egész család.",
     CHRISTMAS_EVE),
    ("hu", "Szenteste idén a nagymamáméknál gyűlünk össze.", CHRISTMAS_EVE),
    ("sl", "Božič bomo letos praznovali pri babici.", CHRISTMAS),
    ("fa", "قرار است کریسمس امسال را کنار مادربزرگ بگذرانیم.", CHRISTMAS),
    ("sv", "Vi har bestämt att fira julafton hos mormor i år.",
     CHRISTMAS_EVE),
    ("nb", "Vi har tenkt å feire nyttårsaften hos besteforeldrene på hytta i år.",
     NEW_YEARS_EVE),
    ("nn", "Vi har tenkt å feire julaftan hjå besteforeldra på landet i år.",
     CHRISTMAS_EVE),
])
def test_this_year_in_the_clause_is_a_cue(lang, text, want):
    assert day(text, lang) == want


@pytest.mark.parametrize("lang,text,want", [
    ("ms", "Kami bercadang untuk berkelah pada Hari Tahun Baru nanti.",
     NEW_YEAR),
    ("eu", "Urteberri egunean mendira igotzeko asmoa dugu lagunekin.",
     NEW_YEAR),
    ("hu", "Karácsony első napján az egész család nálunk ebédel.", CHRISTMAS),
    ("hu", "Húsvétvasárnap a nagymamámnál gyűlik össze az egész család.",
     EASTER),
    ("da", "Vi har aftalt at køre op til mormor i Skagen juledag.", CHRISTMAS),
])
def test_word_for_day_names_a_day(lang, text, want):
    assert day(text, lang) == want


@pytest.mark.parametrize("lang,text", [
    ("fy", "De kat leit op de tafel by it finster."),
    ("el", "Το φετινό κρασί είναι πολύ καλό."),
    ("ru", "Ближайший магазин находится за углом."),
    ("az", "Qarşıdakı evdə nənəm yaşayır."),
    ("sl", "Za babico smo spekli orehovo potico."),
    ("tr", "Doğum günü partisine bütün sınıf geldi."),
    ("hu", "Idén sok hó esett a hegyekben."),
    ("fa", "امسال باران زیادی آمد."),
    ("sl", "Letos je zapadlo veliko snega."),
])
def test_cue_word_in_another_sense_names_no_date(lang, text):
    assert day(text, lang) is None


@pytest.mark.parametrize("lang,text", [
    # "nowruz" and "великден" end in the word for day, but are no compound
    ("fa", "بوی شیرینی‌های خانگی همیشه حال‌وهوای نوروز را برایم زنده می‌کند."),
    ("bg", "Баба ми казва, че козунакът става най-вкусен с много любов към Великден."),
    # "i år" in another clause does not scope the name
    ("sv", "Vi har inte rest någonstans i år, men julafton hos mormor var alltid mysig."),
])
def test_bare_name_without_a_cue_names_no_date(lang, text):
    assert day(text, lang) is None


@pytest.mark.parametrize("lang,text,bare", [
    ("nb", "Dagen etter første nyttårsdag skal vi pakke ned juletreet.",
     NEW_YEAR),
    ("nn", "Dagen før første nyttårsdag skal bestemor bake kransekake.",
     NEW_YEAR),
    ("eu", "Eguberri eguna igaro eta bi egunera, amonaren urtebetetzea ospatuko dugu.",
     CHRISTMAS),
    ("ms", "Kami bercadang membeli bunga api sehari sebelum Hari Tahun Baru.",
     NEW_YEAR),
])
def test_offset_anchor_is_not_read_as_the_bare_holiday(lang, text, bare):
    assert day(text, lang) != bare


def test_year_in_a_coordinate_clause_does_not_scope_the_holiday():
    # issue #1498: the year of the first clause folded into the holiday
    got = day("we met in 2015, and we will meet again at christmas", "en")
    assert got != date(2015, 12, 25)
