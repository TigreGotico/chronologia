"""Adversarial Swahili cases plus the shared English semantic-parity block."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", ["siku", "miaka", "wiki", "dakika"])
def test_a_bare_unit_without_a_count_is_not_an_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["baada ya", "kabla ya", "hadi", "na",
                                  "kutoka", "kati ya"])
def test_a_lone_marker_is_not_a_date(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["uliopita", "iliyopita", "zilizopita",
                                  "ujao", "ijayo", "huu", "hii"])
def test_a_lone_agreement_word_is_not_a_date(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["tano", "mitano", "ishirini na tano",
                                  "mia tatu", "kumi na saba"])
def test_a_bare_numeral_is_not_a_date(text):
    """A count with nothing counted names no time."""
    nomatch(text)


def test_a_spelled_four_figure_numeral_reads_as_a_year():
    """"elfu mbili" is 2000, and a four-figure number is a year everywhere.

    This is the library's own convention, not a Swahili one -- English "two
    thousand" answers the same year from the same anchor -- so the Swahili fold
    is held to it rather than made an exception.
    """
    sw = extract_timespan("elfu mbili", "sw", ANCHOR)
    en = extract_timespan("two thousand", "en", ANCHOR)
    assert sw is not None and en is not None
    assert (sw[0].start, sw[0].end) == (en[0].start, en[0].end)


PAIRS = [
    ("leo", "today"), ("kesho", "tomorrow"), ("jana", "yesterday"),
    ("juzi", "the day before yesterday"), ("kesho kutwa", "overmorrow"),
    ("siku mbili zilizopita", "2 days ago"),
    ("siku tano zilizopita", "5 days ago"),
    ("saa tatu zilizopita", "3 hours ago"),
    ("dakika kumi zilizopita", "10 minutes ago"),
    ("sekunde thelathini zilizopita", "30 seconds ago"),
    ("wiki mbili zilizopita", "2 weeks ago"),
    ("miezi mitatu iliyopita", "3 months ago"),
    ("miaka miwili iliyopita", "2 years ago"),
    ("miaka kumi na moja iliyopita", "11 years ago"),
    ("dakika kumi na tano zilizopita", "15 minutes ago"),
    ("miaka mia moja iliyopita", "100 years ago"),
    ("baada ya siku mbili", "in 2 days"),
    ("baada ya saa tatu", "in 3 hours"),
    ("baada ya dakika arobaini na tano", "in 45 minutes"),
    ("baada ya miaka minne", "in 4 years"),
    ("baada ya wiki mbili", "in 2 weeks"),
    ("mwaka uliopita", "last year"), ("mwaka ujao", "next year"),
    ("mwaka huu", "this year"),
    ("mwezi uliopita", "last month"), ("mwezi ujao", "next month"),
    ("mwezi huu", "this month"),
    ("Jumatatu ijayo", "next monday"),
    ("Ijumaa iliyopita", "last friday"),
    ("Jumatano ijayo", "next wednesday"),
    ("09:30", "09:30"), ("00:00", "00:00"), ("21:50", "21:50"),
    ("14:05", "14:05"),
    ("2027", "2027"), ("1918", "1918"),
    ("5 Juni 2027", "5 june 2027"),
    ("25 Desemba 2020", "25 december 2020"),
    ("1 Januari 2030", "1 january 2030"),
    ("15 Agosti 2027", "15 august 2027"),
    ("Julai 2027", "july 2027"),
]


@pytest.mark.parametrize("sw_text,en_text", PAIRS)
def test_span_parity(sw_text, en_text):
    sw = extract_timespan(sw_text, "sw", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert sw is not None, f"sw {sw_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert sw[0].start == en[0].start and sw[0].end == en[0].end, (sw_text,
                                                                   en_text)
