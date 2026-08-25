"""Bare durations, where the count follows its unit.

``extract_duration`` answers a different question from ``extract_timespan``:
how long, not when.  It takes no anchor and returns a :class:`timedelta`, so it
cannot name a time of day and the six-hour sunrise offset that makes the
Swahili clock unreadable has nothing to bite on -- three hours of elapsed time
is three hours under either convention.  "saa tatu" therefore reads as a
duration while the same string refuses as a time of day, and the two are pinned
against each other below.

The word order is the locale's real difficulty here.  Swahili is head-initial:
the numeral is a modifier and modifiers follow their head, so a duration is
"siku tano" -- day five -- and never the count-then-unit order every other
locale in the tree spells.
"""
from datetime import timedelta

import pytest

from chronologia import extract_duration, extract_timespan

from ._corpus import ANCHOR, nomatch


def dur(text):
    return extract_duration(text, "sw")


@pytest.mark.parametrize("text,expected", [
    ("sekunde kumi", timedelta(seconds=10)),
    ("sekunde thelathini", timedelta(seconds=30)),
    ("dakika tano", timedelta(minutes=5)),
    ("dakika thelathini", timedelta(minutes=30)),
    ("dakika arobaini na tano", timedelta(minutes=45)),
    ("saa moja", timedelta(hours=1)),
    ("saa tatu", timedelta(hours=3)),
    ("saa kumi na mbili", timedelta(hours=12)),
    ("siku tano", timedelta(days=5)),
    ("siku saba", timedelta(days=7)),
    ("wiki mbili", timedelta(days=14)),
    ("wiki tatu", timedelta(days=21)),
])
def test_the_count_follows_its_unit(text, expected):
    r = dur(text)
    assert r is not None, f"{text!r} read as no duration at all"
    assert r.duration == expected
    assert r.remainder == ""


@pytest.mark.parametrize("text,expected", [
    ("saa 3", timedelta(hours=3)),
    ("siku 5", timedelta(days=5)),
    ("dakika 45", timedelta(minutes=45)),
])
def test_a_digit_count_reads_in_the_same_position(text, expected):
    assert dur(text).duration == expected


def test_components_sum():
    assert dur("siku tano na saa tatu").duration == timedelta(days=5, hours=3)


@pytest.mark.parametrize("text,expected", [
    ("saa tatu na nusu", timedelta(hours=3, minutes=30)),
    ("siku tano na nusu", timedelta(days=5, hours=12)),
    ("saa nane na robo", timedelta(hours=8, minutes=15)),
])
def test_the_trailing_fraction_attaches(text, expected):
    """"saa tatu na nusu" is three and a half hours, not three.

    Truncating the fraction and leaving "na nusu" in the remainder would be the
    same defect shape as answering a day-part band for a named hour: a wrong
    length with the missing part visible beside it.
    """
    r = dur(text)
    assert r.duration == expected
    assert r.remainder == ""


@pytest.mark.parametrize("text,expected", [
    ("nusu saa", timedelta(minutes=30)),
    ("robo saa", timedelta(minutes=15)),
])
def test_a_leading_fraction_scales_the_unit(text, expected):
    assert dur(text).duration == expected


@pytest.mark.parametrize("text", ["miezi mitatu", "miaka mitano", "mwaka moja"])
def test_the_calendar_units_are_not_durations(text):
    """A month and a year are not fixed widths, here as in every locale."""
    assert dur(text) is None


@pytest.mark.parametrize("text", ["siku", "saa", "dakika", "tano", "mitano"])
def test_a_unit_or_a_count_alone_is_no_duration(text):
    assert dur(text) is None


def test_the_unit_first_order_is_this_locale_and_no_other():
    """A count-first locale must not gain a unit-first reading.

    The order is declared by ``duration_count_follows_unit`` in ``lang.json``;
    without the gate every locale would start reading "days 5" as five days.
    """
    from chronologia.extract.loader import load_lang_spec
    assert load_lang_spec("sw").conventions.duration_count_follows_unit
    for other in ("en", "mk", "id"):
        assert not load_lang_spec(other).conventions.duration_count_follows_unit
    assert extract_duration("days 5", "en") is None
    assert extract_duration("часа три", "mk") is None


@pytest.mark.parametrize("text,expected", [
    ("saa tatu", timedelta(hours=3)),
    ("saa sita", timedelta(hours=6)),
    ("saa kumi na mbili", timedelta(hours=12)),
])
def test_saa_reads_as_a_length_while_refusing_as_a_time(text, expected):
    """The whole judgement of this locale, stated in one assertion.

    The same string is answerable as a length and unanswerable as a time.  A
    duration carries no convention -- three hours is three hours whether the
    writer counts from sunrise or from midnight -- so there is no six-hour
    error available on this path and refusing it would be refusing something
    that is not ambiguous.  A time of day carries the convention, cannot be
    told which one is meant, and refuses.
    """
    assert dur(text).duration == expected
    nomatch(text)
    assert extract_timespan(text, "sw", ANCHOR) is None


def test_the_hour_length_is_not_shifted_by_six():
    """The sunrise offset must not leak onto the duration path either."""
    assert dur("saa sita").duration == timedelta(hours=6)
    assert dur("saa moja").duration == timedelta(hours=1)
