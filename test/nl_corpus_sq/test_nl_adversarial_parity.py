"""Adversarial Albanian cases plus the shared English semantic-parity block."""
import pytest

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", [
    "", "   ", "përshëndetje si je", "qwerty zxcvb", "këtu nuk ka datë",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text,word", [
    ("prije tri dana", "dana"), ("пре три дана", "дана"),
    ("acum trei zile", "zile"), ("πριν τρεις ημέρες", "ημέρες"),
    ("domani", "domani"), ("wczoraj", "wczoraj"),
])
def test_foreign_not_matched(text, word):
    """Balkan neighbours whose temporal vocabulary sits next to Albanian's on
    every map but shares none of its surfaces: the foreign unit word is never
    consumed, so no foreign offset can resolve."""
    r = parse(text)
    assert r is None or word in r[1]


@pytest.mark.parametrize("text", ["ditësh më parë", "pas javësh"])
def test_a_plural_unit_without_a_count_is_not_an_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_a_month_name_inside_a_word_is_not_a_month():
    nomatch("majtist")


def test_the_connective_alone_is_not_a_clock():
    nomatch("e")


def test_pa_alone_is_not_a_clock():
    nomatch("pa")


PAIRS = [
    ("sot", "today"), ("nesër", "tomorrow"), ("dje", "yesterday"),
    ("pasnesër", "overmorrow"), ("pardje", "ereyesterday"),
    ("pas një dite", "in 1 day"), ("pas tri ditësh", "in 3 days"),
    ("pas dy javësh", "in 2 weeks"), ("pas dy muajsh", "in 2 months"),
    ("pas pesë vjetësh", "in 5 years"),
    ("pas pesëmbëdhjetë minutash", "in 15 minutes"),
    ("pas dhjetë orësh", "in 10 hours"),
    ("tre ditë më parë", "3 days ago"),
    ("njëmbëdhjetë vjet më parë", "11 years ago"),
    ("njëzet e një vjet më parë", "21 years ago"),
    ("të premten e ardhshme", "next friday"),
    ("të hënën e ardhshme", "next monday"),
    ("të martën e kaluar", "last tuesday"),
    ("javën e kaluar", "last week"),
    ("javën e ardhshme", "next week"),
    ("muajin e kaluar", "last month"),
    ("muajin e ardhshëm", "next month"),
    ("vjet", "last year"), ("sivjet", "this year"), ("mot", "next year"),
    ("15:30", "15:30"), ("09:30", "09:30"), ("00:00", "00:00"),
    ("mesditë", "noon"), ("mesnatë", "midnight"),
    ("shtatë e gjysmë", "half past seven"),
    ("tre pa çerek", "quarter to three"),
    ("dy e çerek", "quarter past two"),
    ("2019", "2019"), ("1918", "1918"),
    ("5 korrik 2027", "july 5 2027"),
    ("qershor 2027", "june 2027"),
    ("vera 2020", "summer 2020"),
    ("e mërkurë", "wednesday"),
]
