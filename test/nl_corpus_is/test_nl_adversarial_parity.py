"""Adversarial Icelandic cases plus the shared English semantic-parity block."""
from datetime import timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse, span


@pytest.mark.parametrize("text", [
    "", "   ", "halló hvað segirðu", "qwerty zxcvb", "hér er engin dagsetning",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "þrír dagar", "fimm dagar", "tvær vikur", "tíu ár", "3 dagar",
])
def test_offset_without_marker(text):
    """A bare count of units is a quantity, not a point in time."""
    nomatch(text)


@pytest.mark.parametrize("text", ["fyrir", "eftir", "dagar", "fyrir dögum"])
def test_incomplete_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", [
    "for tre dager siden", "för tre dagar sedan", "in drei Tagen", "i morgen",
])
def test_germanic_siblings_not_matched(text):
    """Norwegian, Swedish, German and Danish phrasings share roots with
    Icelandic but must not read as it."""
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_german_vor_is_the_icelandic_spring():
    """The German offset marker "vor" is spelled like the Icelandic word for
    spring, so a German phrase reads its first word as a season rather than
    as an offset -- the season wins and the rest is left unread."""
    s = span("vor drei Tagen")
    assert (s.start.month, s.end.month) == (3, 6)
    assert "drei" in parse("vor drei Tagen")[1]


def test_bare_numeral_is_not_a_year():
    """A spelled numeral folds to a digit, but a small digit is not a year."""
    nomatch("tuttugu og fimm")


def test_og_alone_joins_nothing():
    nomatch("og")


def test_two_separate_numbers_do_not_fuse():
    """"og" only continues a numeral when the word after it is a smaller
    magnitude; "fimm og fimm" is two fives, not ten."""
    nomatch("fimm og fimm")


def test_bare_weekday_resolves_next():
    # a bare weekday names its next strictly-future occurrence, a day-wide span
    ahead = (4 - ANCHOR.weekday()) % 7 or 7          # 4 == Friday (föstudagur)
    s = (ANCHOR + timedelta(days=ahead)).date()
    e = s + timedelta(days=1)
    sp = span("föstudagur")
    assert (sp.start.year, sp.start.month, sp.start.day) == (s.year, s.month, s.day)
    assert (sp.end.year, sp.end.month, sp.end.day) == (e.year, e.month, e.day)


PAIRS = [
    ("í dag", "today"), ("á morgun", "tomorrow"), ("í gær", "yesterday"),
    ("í fyrradag", "ereyesterday"),
    ("eftir einn dag", "in 1 day"), ("eftir þrjá daga", "in 3 days"),
    ("eftir tvær vikur", "in 2 weeks"), ("eftir tvo mánuði", "in 2 months"),
    ("eftir fimm ár", "in 5 years"),
    ("eftir fimmtán mínútur", "in 15 minutes"),
    ("eftir tíu klukkustundir", "in 10 hours"),
    ("eftir tuttugu og fimm daga", "in 25 days"),
    ("fyrir þremur dögum", "3 days ago"), ("fyrir einni viku", "1 week ago"),
    ("fyrir tveimur árum", "2 years ago"),
    ("fyrir hundrað árum", "100 years ago"),
    ("næsta föstudag", "next friday"), ("næsta mánudag", "next monday"),
    ("síðastliðinn þriðjudag", "last tuesday"),
    ("15:30", "15:30"), ("09:30", "09:30"), ("00:00", "00:00"),
    ("hádegi", "noon"), ("miðnætti", "midnight"),
    ("klukkan þrjú", "at three"),
    ("kortér yfir tvö", "quarter past two"),
    ("hálf tvö", "half past one"),
    ("2019", "2019"), ("1918", "1918"), ("2017-06-30", "2017-06-30"),
    ("5. júní", "june 5"), ("fimmti júní", "june 5"),
    ("25. desember 2020", "25 december 2020"),
    ("sumar 2020", "summer 2020"), ("næsta helgi", "next weekend"),
    ("laugardagur", "saturday"),
]


@pytest.mark.parametrize("is_text,en_text", PAIRS)
def test_span_parity(is_text, en_text):
    ice = extract_timespan(is_text, "is", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert ice is not None, f"is {is_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert ice[0].start == en[0].start and ice[0].end == en[0].end, (
        is_text, en_text)
