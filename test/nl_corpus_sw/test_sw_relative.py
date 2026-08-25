"""Relative time: the agreement word that trails every unit.

Swahili says "last" and "next" with a relative verb form agreeing with the
noun class of what it modifies, and it says them AFTER the noun.  Year and
month are class 3/4 and take uliopita / huu / ujao; week, hour, minute, second
and every weekday are class 9/10 and take iliyopita / hii / ijayo, with
zilizopita as the class 9/10 plural.

The same words do double duty.  There is no separate word for "ago": CLDR
spells N years ago as "miaka {0} iliyopita", the unit noun, the count, and the
same relative form that spells "mwaka uliopita" on its own.  So the marker that
selects a calendar period also closes a counted offset, and the two readings
are told apart by whether a count stands between the noun and the marker.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, day, nomatch, parse, span, start, start_end


# -- named days --------------------------------------------------------------

@pytest.mark.parametrize("text,date", [
    ("leo", (2027, 5, 12)), ("kesho", (2027, 5, 13)),
    ("jana", (2027, 5, 11)), ("juzi", (2027, 5, 10)),
    ("kesho kutwa", (2027, 5, 14)),
])
def test_named_days(text, date):
    assert start_end(text) == day(*date)


def test_the_two_day_names_are_two_words_and_one_word():
    """juzi is a single word, kesho kutwa two -- both name a two-day step."""
    assert start_end("juzi") == day(2027, 5, 10)
    assert start_end("kesho kutwa") == day(2027, 5, 14)


# -- calendar periods, marker trailing --------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("mwaka uliopita", (2026, 1, 1)),
    ("mwaka huu", (2027, 1, 1)),
    ("mwaka ujao", (2028, 1, 1)),
    ("mwezi uliopita", (2027, 4, 1)),
    ("mwezi huu", (2027, 5, 1)),
    ("mwezi ujao", (2027, 6, 1)),
])
def test_the_class_three_units_take_the_u_forms(text, expected):
    s = start(text)
    assert (s.year, s.month, s.day) == expected


@pytest.mark.parametrize("text,expected", [
    ("wiki iliyopita", (2027, 5, 1)),
    ("wiki hii", (2027, 5, 8)),
    ("wiki ijayo", (2027, 5, 15)),
])
def test_the_class_nine_unit_takes_the_i_forms(text, expected):
    s = start(text)
    assert (s.year, s.month, s.day) == expected


@pytest.mark.parametrize("text", [
    "uliopita mwaka", "ujao mwezi", "ijayo wiki", "iliyopita Jumatatu",
])
def test_the_marker_never_leads_its_noun(text):
    """Swahili is noun-first; the preposed order is not Swahili at all.

    The base grammar offers a marker-leading order to every locale, and this
    one opts out of it, so the ungrammatical string must not resolve to the
    period the grammatical one names.
    """
    r = parse(text)
    assert r is None or r[1] != "", (
        f"{text!r} was read as a period with the marker leading")


# -- counted offsets ---------------------------------------------------------

@pytest.mark.parametrize("phrase,delta", [
    ("sekunde thelathini zilizopita", timedelta(seconds=30)),
    ("dakika tano zilizopita", timedelta(minutes=5)),
    ("dakika arobaini na tano zilizopita", timedelta(minutes=45)),
    ("saa mbili zilizopita", timedelta(hours=2)),
    ("saa kumi na mbili zilizopita", timedelta(hours=12)),
    ("siku saba zilizopita", timedelta(days=7)),
    ("wiki tatu zilizopita", timedelta(days=21)),
])
def test_the_count_stands_between_the_noun_and_the_marker(phrase, delta):
    assert span(phrase).start == ANCHOR - delta


@pytest.mark.parametrize("phrase,delta", [
    ("baada ya sekunde thelathini", timedelta(seconds=30)),
    ("baada ya dakika tano", timedelta(minutes=5)),
    ("baada ya saa mbili", timedelta(hours=2)),
    ("baada ya siku saba", timedelta(days=7)),
    ("baada ya wiki tatu", timedelta(days=21)),
])
def test_baada_ya_opens_a_forward_offset(phrase, delta):
    assert span(phrase).start == ANCHOR + delta


@pytest.mark.parametrize("phrase,years", [
    ("miaka miwili iliyopita", 2), ("miaka mitano iliyopita", 5),
    ("miaka kumi iliyopita", 10), ("miaka ishirini iliyopita", 20),
    ("miaka mia moja iliyopita", 100),
])
def test_years_ago_take_the_plural_noun(phrase, years):
    assert start(phrase).year == ANCHOR.year - years


@pytest.mark.parametrize("phrase,months", [
    ("miezi miwili iliyopita", 2), ("miezi sita iliyopita", 6),
    ("miezi kumi na mbili iliyopita", 12),
])
def test_months_ago_take_the_plural_noun(phrase, months):
    s = start(phrase)
    total = (ANCHOR.year * 12 + ANCHOR.month - 1) - months
    assert (s.year, s.month) == (total // 12, total % 12 + 1)


def test_the_singular_noun_counts_one():
    """CLDR's own singular pattern: "mwaka {0} uliopita" for exactly one.

    The singular takes the singular noun -- mwaka, not miaka -- and the count
    of one, whether written as a digit or spelled with the stem moja.
    """
    assert start("mwaka 1 uliopita").year == ANCHOR.year - 1
    assert start("mwaka moja uliopita").year == ANCHOR.year - 1
    assert start("mwezi 1 uliopita").month == 4
    assert span("siku moja iliyopita").start == ANCHOR - timedelta(days=1)


# -- ranges ------------------------------------------------------------------

def test_a_range_between_two_dates():
    assert start_end("kutoka 5 Juni hadi 8 Juni") == (day(2027, 6, 5)[0],
                                                      day(2027, 6, 9)[0])


def test_a_range_between_two_weekdays():
    assert start_end("kutoka Jumatatu hadi Ijumaa") == (day(2027, 5, 17)[0],
                                                        day(2027, 5, 22)[0])


def test_a_between_range_uses_na_for_its_second_bound():
    assert start_end("kati ya 5 Juni na 8 Juni") == (day(2027, 6, 5)[0],
                                                     day(2027, 6, 9)[0])


def test_mpaka_closes_a_range_as_hadi_does():
    assert start_end("kutoka 5 Juni mpaka 8 Juni") == (day(2027, 6, 5)[0],
                                                       day(2027, 6, 9)[0])


def test_a_lone_relative_verb_form_names_nothing():
    for text in ("uliopita", "ijayo", "hii", "zilizopita"):
        nomatch(text)


# -- open ranges -------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("tangu jana", (2027, 5, 11)),
    ("tangu Jumatatu", (2027, 5, 10)),
    ("tangu 5 Juni", (2026, 6, 5)),
    ("tangu Juni", (2026, 6, 1)),
])
def test_tangu_opens_a_stretch_reaching_up_to_the_anchor(text, expected):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == expected
    assert (e.year, e.month, e.day, e.hour, e.minute) == (
        ANCHOR.year, ANCHOR.month, ANCHOR.day, ANCHOR.hour, ANCHOR.minute)


def test_hadi_closes_a_stretch_running_out_from_the_anchor():
    s, e = start_end("hadi 5 Juni")
    assert (s.year, s.month, s.day, s.hour) == (2027, 5, 12, 13)
    assert (e.year, e.month, e.day) == (2027, 6, 6)
