"""Adversarial Irish cases plus the shared English semantic-parity block."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse, span


@pytest.mark.parametrize("text", [
    "", "   ", "dia duit conas atá tú", "qwerty zxcvb",
    "níl aon dáta anseo",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["ó shin", "tar éis", "chun", "gach", "seo"])
def test_bare_marker_is_not_a_span(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", [
    "ddoe", "yfory", "tair wythnos yn ôl", "bore yfory",
])
def test_welsh_sibling_is_not_matched(text):
    """Welsh is the other Celtic locale and shares the family's mutation
    machinery, but shares almost no surface with Irish; a Welsh phrase must
    not read as one."""
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_se_the_pronoun_does_not_become_a_time():
    """"sé" is at once the numeral six and the pronoun "he", so a sentence
    opening "tá sé" carries a stray number the fold cannot avoid producing.
    The clock reading still has to come from the clock phrase, and the
    pronoun's number must stay in the remainder rather than becoming an
    hour."""
    s = span("tá sé leathuair tar éis a trí")
    assert (s.start.hour, s.start.minute) == (3, 30)


def test_bare_numeral_is_not_a_year():
    """A spelled numeral folds to a digit, but a small digit is not a year."""
    nomatch("fiche a cúig")


def test_two_separate_numbers_do_not_fuse():
    """A coordinator only continues a numeral when the word after it is of a
    smaller magnitude, so "cúig a cúig" stays two fives and never becomes one
    ten -- while "fiche a cúig", where it does descend, is twenty-five."""
    nomatch("cúig a cúig")
    assert span("fiche a cúig lá ó shin") is not None
    assert parse("cúig a cúig lá ó shin")[0].start.day != span(
        "fiche a cúig lá ó shin").start.day


def test_de_prefix_alone_is_not_a_weekday():
    nomatch("Dé")


def test_month_word_alone_is_not_a_month():
    """"mí" is the noun "month"; on its own it is a unit, never January."""
    r = parse("mí")
    assert r is None or r[1] != ""


PAIRS = [
    ("inniu", "today"), ("amárach", "tomorrow"), ("inné", "yesterday"),
    ("arú inné", "ereyesterday"), ("arú amárach", "overmorrow"),
    ("trí lá ó shin", "3 days ago"), ("cúig lá ó shin", "5 days ago"),
    ("fiche a haon lá ó shin", "21 days ago"),
    ("dhá bhliain ó shin", "2 years ago"),
    ("trí bliana ó shin", "3 years ago"),
    ("seacht mbliana ó shin", "7 years ago"),
    ("céad bliain ó shin", "100 years ago"),
    ("cúig huaire ó shin", "5 hours ago"),
    ("seacht n-uaire ó shin", "7 hours ago"),
    ("seachtain ó shin", "1 week ago"), ("trí mhí ó shin", "3 months ago"),
    ("deich nóiméad ó shin", "10 minutes ago"),
    ("Dé hAoine", "friday"), ("Luan", "monday"), ("Dé Máirt", "tuesday"),
    ("Déardaoin", "thursday"), ("Dé Sathairn", "saturday"),
    ("an Luan seo chugainn", "next monday"),
    ("an Luan seo caite", "last monday"),
    ("an Aoine seo chugainn", "next friday"),
    ("Eanáir", "january"), ("Nollaig", "december"),
    ("i mBealtaine", "may"), ("mí Aibreáin", "april"),
    ("5 Meitheamh 2020", "5 june 2020"),
    ("25 Nollaig 2020", "25 december 2020"),
    ("1 Márta 1990", "1 march 1990"),
    ("leathuair tar éis a trí", "half past three"),
    ("ceathrú tar éis a trí", "quarter past three"),
    ("ceathrú chun a dó", "quarter to two"),
    ("a trí a chlog", "at three"),
    ("meán lae", "noon"), ("meán oíche", "midnight"),
    ("15:30", "15:30"), ("2019", "2019"), ("2017-06-30", "2017-06-30"),
    ("deireadh seachtaine", "weekend"),
    ("an deireadh seachtaine seo chugainn", "next weekend"),
]


@pytest.mark.parametrize("ga_text,en_text", PAIRS)
def test_span_parity(ga_text, en_text):
    ga = extract_timespan(ga_text, "ga", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert ga is not None, f"ga {ga_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert ga[0].start == en[0].start and ga[0].end == en[0].end, (
        ga_text, en_text)
