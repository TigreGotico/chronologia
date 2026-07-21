"""Adversarial Ukrainian cases plus the shared English semantic-parity block."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, parse, nomatch


@pytest.mark.parametrize("text", [
    "", "   ", "привіт як справи", "qwerty zxcvb", "немає дати тут",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "три дні", "п'ять років", "два тижні", "десять хвилин",
])
def test_offset_without_marker(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["через 2", "2 тому"])
def test_incomplete_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


# Russian / Polish phrases must not parse as Ukrainian
@pytest.mark.parametrize("text", [
    "через 3 недели",    # ru (недели; uk uses тижні)
    "za 5 lat",          # pl
    "před 2 lety",       # cs
])
def test_foreign_not_matched(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_seconds_offset_gap():
    nomatch("через 45 секунд")


def test_bare_weekday_alone():
    nomatch("п'ятниця")


PAIRS = [
    ("сьогодні", "today"), ("завтра", "tomorrow"), ("вчора", "yesterday"),
    ("післязавтра", "overmorrow"), ("позавчора", "ereyesterday"),
    ("через 3 дні", "in 3 days"), ("через 2 тижні", "in 2 weeks"),
    ("через 1 день", "in 1 day"), ("через 2 місяці", "in 2 months"),
    ("через 5 років", "in 5 years"), ("через 15 хвилин", "in 15 minutes"),
    ("наступна п'ятниця", "next friday"),
    ("наступний понеділок", "next monday"),
    ("минулий вівторок", "last tuesday"), ("15:30", "15:30"),
    ("09:30", "09:30"), ("00:00", "00:00"), ("полудень", "noon"),
    ("північ", "midnight"), ("2019", "2019"), ("1991", "1991"),
    ("2017-06-30", "2017-06-30"),
    ("з червня до серпня", "from june to august"),
    ("з січня до березня", "from january to march"),
    ("між червнем і вереснем", "between june and september"),
    ("літо 2020", "summer 2020"), ("наступна зима", "next winter"),
]


@pytest.mark.parametrize("uk_text,en_text", PAIRS)
def test_span_parity(uk_text, en_text):
    uk = extract_timespan(uk_text, "uk", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert uk is not None, f"uk {uk_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert uk[0].start == en[0].start and uk[0].end == en[0].end, (uk_text, en_text)
