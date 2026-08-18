"""Adversarial Lithuanian cases plus the shared English semantic-parity block."""
from datetime import timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse, span


@pytest.mark.parametrize("text", [
    "", "   ", "labas kaip sekasi", "qwerty zxcvb", "čia nėra datos",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "trys dienos", "penkios dienos", "dvi savaitės", "dešimt metų", "3 dienos",
])
def test_offset_without_marker(text):
    """A bare count of units is a quantity, not a point in time."""
    nomatch(text)


@pytest.mark.parametrize("text", ["prieš", "po", "dienos", "prieš dienas"])
def test_incomplete_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", [
    "przed 2 laty", "через 3 дня", "pirms 3 dienam", "rytdien",
])
def test_foreign_not_matched(text):
    """Polish, Russian and Latvian phrasings must not read as Lithuanian."""
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_seconds_offset_gap():
    nomatch("po 45 sekundžių")


def test_bare_weekday_resolves_next():
    # a bare weekday names its next strictly-future occurrence, a day-wide span
    ahead = (4 - ANCHOR.weekday()) % 7 or 7          # 4 == Friday (penktadienis)
    s = (ANCHOR + timedelta(days=ahead)).date()
    e = s + timedelta(days=1)
    sp = span("penktadienis")
    assert (sp.start.year, sp.start.month, sp.start.day) == (s.year, s.month, s.day)
    assert (sp.end.year, sp.end.month, sp.end.day) == (e.year, e.month, e.day)


PAIRS = [
    ("šiandien", "today"), ("rytoj", "tomorrow"), ("vakar", "yesterday"),
    ("poryt", "overmorrow"), ("užvakar", "ereyesterday"),
    ("po 1 dienos", "in 1 day"), ("po 3 dienų", "in 3 days"),
    ("po 2 savaičių", "in 2 weeks"), ("po 2 mėnesių", "in 2 months"),
    ("po 5 metų", "in 5 years"), ("po 15 minučių", "in 15 minutes"),
    ("po 10 valandų", "in 10 hours"), ("prieš 3 dienas", "3 days ago"),
    ("kitą penktadienį", "next friday"), ("kitą pirmadienį", "next monday"),
    ("praeitą antradienį", "last tuesday"),
    ("15:30", "15:30"), ("09:30", "09:30"), ("00:00", "00:00"),
    ("vidurdienis", "noon"), ("vidurnaktis", "midnight"),
    ("2019", "2019"), ("1918", "1918"), ("2017-06-30", "2017-06-30"),
    ("nuo birželio iki rugpjūčio", "from june to august"),
    ("nuo sausio iki kovo", "from january to march"),
    ("tarp birželio ir rugsėjo", "between june and september"),
    ("vasara 2020", "summer 2020"), ("kita žiema", "next winter"),
    ("liepos 5 d.", "july 5"),
    ("2020 m. gruodžio 25 d.", "25 december 2020"),
]


@pytest.mark.parametrize("lt_text,en_text", PAIRS)
def test_span_parity(lt_text, en_text):
    lt = extract_timespan(lt_text, "lt", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert lt is not None, f"lt {lt_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert lt[0].start == en[0].start and lt[0].end == en[0].end, (lt_text, en_text)
