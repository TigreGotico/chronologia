"""Spelled numerals: the compound with и, the scale words, and gender-marked one.

Every value asserted here is the arithmetic of the phrase, computed against the
anchor with plain Python and never read back from a parse.  Cardinal one is
gender-marked -- еден before a masculine noun, една before a feminine one -- and
both spell exactly one, which is the whole point of listing both.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, span, start, start_end, nomatch, parse


def ago(**kw):
    return ad(ANCHOR - timedelta(**kw))


def ahead(**kw):
    return ad(ANCHOR + timedelta(**kw))


@pytest.mark.parametrize("text,days", [
    ("пред еден ден", 1),
    ("пред два дена", 2),
    ("пред три дена", 3),
    ("пред четири дена", 4),
    ("пред пет дена", 5),
    ("пред шест дена", 6),
    ("пред седум дена", 7),
    ("пред осум дена", 8),
    ("пред девет дена", 9),
    ("пред десет дена", 10),
    ("пред единаесет дена", 11),
    ("пред дванаесет дена", 12),
    ("пред петнаесет дена", 15),
    ("пред деветнаесет дена", 19),
    ("пред дваесет дена", 20),
    ("пред триесет дена", 30),
    ("пред сто дена", 100),
])
def test_a_spelled_count_of_days(text, days):
    assert start(text) == ago(days=days)


@pytest.mark.parametrize("text,minutes", [
    ("пред дваесет и една минута", 21),
    ("пред дваесет и пет минути", 25),
    ("пред триесет и седум минути", 37),
    ("пред четириесет и пет минути", 45),
    ("пред педесет и девет минути", 59),
])
def test_the_tens_and_unit_compound(text, minutes):
    assert start(text) == ago(minutes=minutes)


@pytest.mark.parametrize("text,years", [
    ("пред илјада години", 1000),
    ("пред две илјади години", 2000),
])
def test_the_thousand_multiplies_the_numeral_before_it(text, years):
    assert start(text).year == ANCHOR.year - years


@pytest.mark.parametrize("text,unit,amount", [
    ("пред една минута", "minutes", 1),
    ("пред една секунда", "seconds", 1),
    ("пред еден ден", "days", 1),
    ("пред еден час", "hours", 1),
])
def test_gender_marked_one_counts_one(text, unit, amount):
    assert start(text) == ago(**{unit: amount})


def test_the_masculine_and_the_feminine_one_read_the_same_value():
    assert start("пред еден час") == start("пред 1 час")
    assert start("пред една минута") == start("пред 1 минута")


@pytest.mark.parametrize("text,minutes", [
    ("за пет минути", 5),
    ("за петнаесет минути", 15),
    ("за дваесет и пет минути", 25),
    ("за четириесет минути", 40),
])
def test_the_same_numerals_read_forward(text, minutes):
    assert start(text) == ahead(minutes=minutes)


def test_the_connector_does_not_join_two_units():
    # и joins a tens word to its unit and nothing else.  Were it allowed to
    # bridge any pair, the clock's own connector would be swallowed and the
    # minute of "девет и пет" would vanish into a single fourteen.
    s = span("девет и пет")
    assert (s.start.hour, s.start.minute) == (9, 5)


def test_a_bare_numeral_is_not_a_date():
    # A four-digit value is the one exception: илјада is a thousand and a bare
    # thousand is a readable year, exactly as the digits 1000 would be.
    for text in ("пет", "дваесет и пет", "четириесет"):
        r = parse(text)
        assert r is None or r[1] != ""
