"""The Armenian cardinal system, which is decimal and writes 21..99 as ONE word.

There is no base-20 grouping and no coordinator anywhere: a tens word joins
its unit directly, with a final ``ը`` on the tens rewritten to ``ն``
(``տասը``+``ինը`` -> ``տասնինը``, ``քսան``+``մեկ`` -> ``քսանմեկ``).  Above 99
the multiplier words ``հարյուր`` and ``հազար`` stand as separate words.
Each surface below is taken from the en.wiktionary.org numeral tables and its
value written out here by hand; the phrase is read through a minute offset so
the assertion is plain clock arithmetic on the anchor.

The spaced spelling of a compound is pinned as a REFUSAL: ``քսան մեկ`` is two
numerals standing side by side, not 21, and the extractor must strand the
first rather than fabricate a compound the language does not write.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start


def _minutes_ago(n):
    return ad(ANCHOR - timedelta(minutes=n))


@pytest.mark.parametrize("word,value", [
    ("զրո", 0), ("մեկ", 1), ("երկու", 2), ("երեք", 3), ("չորս", 4),
    ("հինգ", 5), ("վեց", 6), ("յոթ", 7), ("ութ", 8), ("ինը", 9),
    ("տասը", 10),
])
def test_units(word, value):
    assert start(f"{word} րոպե առաջ") == _minutes_ago(value)


@pytest.mark.parametrize("word,value", [
    ("տասնմեկ", 11), ("տասներկու", 12), ("տասներեք", 13), ("տասնչորս", 14),
    ("տասնհինգ", 15), ("տասնվեց", 16), ("տասնյոթ", 17), ("տասնութ", 18),
    ("տասնինը", 19),
])
def test_teens_join_the_ten_directly(word, value):
    assert start(f"{word} րոպե առաջ") == _minutes_ago(value)


@pytest.mark.parametrize("word,value", [
    ("քսան", 20), ("երեսուն", 30), ("քառասուն", 40), ("հիսուն", 50),
    ("վաթսուն", 60), ("յոթանասուն", 70), ("ութսուն", 80), ("իննսուն", 90),
])
def test_tens(word, value):
    assert start(f"{word} րոպե առաջ") == _minutes_ago(value)


@pytest.mark.parametrize("word,value", [
    ("քսանմեկ", 21), ("քսանհինգ", 25), ("քսանինը", 29),
    ("երեսուներկու", 32), ("երեսունմեկ", 31),
    ("քառասունյոթ", 47), ("հիսունութ", 58), ("վաթսուներեք", 63),
    ("յոթանասունվեց", 76), ("ութսունչորս", 84), ("իննսունինը", 99),
])
def test_compounds_are_one_word(word, value):
    assert start(f"{word} րոպե առաջ") == _minutes_ago(value)


@pytest.mark.parametrize("phrase,value", [
    ("հարյուր", 100),
    ("երկու հարյուր", 200),
    ("ինը հարյուր", 900),
    ("հազար", 1000),
])
def test_multipliers_stand_as_separate_words(phrase, value):
    assert start(f"{phrase} րոպե առաջ") == _minutes_ago(value)


@pytest.mark.parametrize("text,stranded", [
    ("քսան մեկ րոպե առաջ", "քսան"),
    ("երեսուն երկու րոպե առաջ", "երեսուն"),
])
def test_a_spaced_compound_is_not_one_numeral(text, stranded):
    """Armenian writes 21 as քսանմեկ; two numerals separated by a space are
    two numerals, so the leading one is left unread instead of being folded
    into a compound the orthography does not have."""
    r = parse(text)
    assert r is not None
    assert stranded in r[1]


@pytest.mark.parametrize("text", [
    "քսան և մեկ րոպե առաջ", "քսան ու մեկ րոպե առաջ",
])
def test_no_coordinator_joins_a_numeral(text):
    """No connector appears inside an Armenian numeral at any magnitude, so
    a coordinated pair must never read as their sum."""
    r = parse(text)
    assert r is None or r[1] != ""
    if r is not None:
        assert r[0].start != _minutes_ago(21)


@pytest.mark.parametrize("word,century", [
    ("տասնիններորդ", 19), ("քսաներորդ", 20),
])
def test_ordinals_take_the_eastern_suffix(word, century):
    """The ordinal suffix is ``-երորդ``, or ``-ներորդ`` replacing a final
    ``ը``.  This is the EASTERN series; Western Armenian's ``-երթ`` belongs to
    a different locale and is not read here."""
    s = start(f"{word} դար")
    assert (s.year, s.month, s.day) == ((century - 1) * 100, 1, 1)


@pytest.mark.parametrize("word", ["քսաներթ", "տասներթ", "հինգերթ"])
def test_western_ordinals_are_not_read(word):
    r = parse(f"{word} դար")
    assert r is None or word in r[1]
