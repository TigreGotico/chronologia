"""Adversarial Macedonian cases plus the shared English semantic-parity block."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", ["дена ", "години", "часа", "минути"])
def test_a_plural_unit_without_a_count_is_not_an_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_a_lone_marker_is_not_a_date():
    for text in ("пред", "за", "до", "и", "од"):
        nomatch(text)


def test_a_lone_relative_word_is_not_a_date():
    for text in ("минатиот", "следната", "оваа"):
        nomatch(text)


PAIRS = [
    ("денес", "today"), ("утре", "tomorrow"), ("вчера", "yesterday"),
    ("задутре", "overmorrow"), ("завчера", "the day before yesterday"),
    ("пред 2 дена", "2 days ago"), ("пред 5 дена", "5 days ago"),
    ("пред 3 часа", "3 hours ago"), ("пред 10 минути", "10 minutes ago"),
    ("пред 30 секунди", "30 seconds ago"),
    ("пред 2 седмици", "2 weeks ago"), ("пред 3 месеци", "3 months ago"),
    ("пред 2 години", "2 years ago"),
    ("пред единаесет години", "11 years ago"),
    ("пред петнаесет минути", "15 minutes ago"),
    ("за 2 дена", "in 2 days"), ("за 3 часа", "in 3 hours"),
    ("за 45 минути", "in 45 minutes"), ("за 4 години", "in 4 years"),
    ("лани", "last year"), ("догодина", "next year"),
    ("оваа година", "this year"),
    ("минатиот месец", "last month"), ("следниот месец", "next month"),
    ("овој месец", "this month"),
    ("минатата седмица", "last week"), ("следната седмица", "next week"),
    ("следниот понеделник", "next monday"),
    ("минатиот петок", "last friday"),
    ("09:30", "09:30"), ("00:00", "00:00"), ("21:50", "21:50"),
    ("девет и пол", "half past nine"),
    ("2027", "2027"), ("1918", "1918"),
    ("5 јуни 2027", "5 june 2027"),
    ("25 декември 2020", "25 december 2020"),
    ("1 јануари 2030", "1 january 2030"),
    ("15 август 2027", "15 august 2027"),
    ("пладне", "noon"), ("полноќ", "midnight"),
]


@pytest.mark.parametrize("mk_text,en_text", PAIRS)
def test_span_parity(mk_text, en_text):
    mk = extract_timespan(mk_text, "mk", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert mk is not None, f"mk {mk_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert mk[0].start == en[0].start and mk[0].end == en[0].end, (mk_text,
                                                                   en_text)
