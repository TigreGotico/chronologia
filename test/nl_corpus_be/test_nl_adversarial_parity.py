"""Adversarial Belarusian cases plus the shared English semantic-parity block."""
from datetime import timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", [
    "", "   ", "прывітанне як справы", "qwerty zxcvb", "тут няма даты",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", [
    "через 3 дня", "завтра", "вчера", "через 5 минут", "za tydzień",
    "післязавтра", "три дня назад",
])
def test_foreign_not_matched(text):
    """Russian, Polish and Ukrainian phrasings must not read as Belarusian --
    Russian above all, whose surfaces look close enough to invite a false
    match and whose two unit words this locale deliberately does not share."""
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["дзён таму", "праз тыдні", "хвілін таму"])
def test_a_plural_unit_without_a_count_is_not_an_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_a_month_name_inside_a_word_is_not_a_month():
    nomatch("маёвы")


def test_a_weekday_inside_a_word_is_not_a_weekday():
    nomatch("серадзінны")


@pytest.mark.parametrize("text", ["за гадзіну", "за дзве гадзіны",
                                  "за пяць дзён"])
def test_the_clock_direction_word_does_not_hijack_a_duration(text):
    """"за" carries the subtractive clock only in front of a fraction or a
    minute count followed by an hour; on its own in front of a duration it
    must not fabricate a time."""
    r = parse(text)
    assert r is None or r[0].end - r[0].start != timedelta(minutes=1)


@pytest.mark.parametrize("text", ["з 5 да 12 ліпеня", "да 5 ліпеня"])
def test_da_still_opens_a_range(text):
    """The control that keeps да out of the clock: it must go on reading as
    the ordinary range end."""
    assert parse(text) is not None


PAIRS = [
    ("сёння", "today"), ("заўтра", "tomorrow"), ("учора", "yesterday"),
    ("паслязаўтра", "overmorrow"), ("пазаўчора", "ereyesterday"),
    ("праз 1 дзень", "in 1 day"), ("праз 3 дні", "in 3 days"),
    ("праз 2 тыдні", "in 2 weeks"), ("праз 2 месяцы", "in 2 months"),
    ("праз 5 гадоў", "in 5 years"), ("праз 15 хвілін", "in 15 minutes"),
    ("праз 10 гадзін", "in 10 hours"), ("3 дні таму", "3 days ago"),
    ("11 гадоў таму", "11 years ago"), ("21 год таму", "21 years ago"),
    ("наступная пятніца", "next friday"),
    ("наступны панядзелак", "next monday"),
    ("мінулы аўторак", "last tuesday"),
    ("15:30", "15:30"), ("09:30", "09:30"), ("00:00", "00:00"),
    ("апоўдні", "noon"), ("апоўначы", "midnight"),
    ("2019", "2019"), ("1918", "1918"), ("2017-06-30", "2017-06-30"),
    ("лета 2020", "summer 2020"), ("наступная зіма", "next winter"),
    ("5 ліпеня", "july 5"), ("25 снежня 2020", "25 december 2020"),
    ("20-е стагоддзе", "the 20th century"),
    ("мінулы тыдзень", "last week"), ("наступны месяц", "next month"),
    ("гэты год", "this year"), ("другі квартал 2020", "q2 2020"),
    ("без чвэрці адзінаццаць", "quarter to eleven"),
    ("палова на пятую", "half past four"),
    ("летась", "last year"), ("сёлета", "this year"),
    ("у наступным годзе", "next year"),
    ("на мінулым тыдні", "last week"),
    ("у мінулым месяцы", "last month"),
]


@pytest.mark.parametrize("be_text,en_text", PAIRS)
def test_span_parity(be_text, en_text):
    be = extract_timespan(be_text, "be", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert be is not None, f"be {be_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert be[0].start == en[0].start and be[0].end == en[0].end, \
        (be_text, en_text)
