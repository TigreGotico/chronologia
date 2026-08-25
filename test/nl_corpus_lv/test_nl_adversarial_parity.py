"""Adversarial Latvian cases plus the shared English semantic-parity block."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", [
    "", "   ", "sveiki kā iet", "qwerty zxcvb", "šeit nav datuma",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", [
    "prieš 3 dienas", "po trijų dienų", "przed 2 laty", "через 3 дня",
    "rytoj", "šiandien",
])
def test_foreign_not_matched(text):
    """Lithuanian, Polish and Russian phrasings must not read as Latvian --
    the sibling Baltic language above all, whose surfaces look close enough
    to invite a false match."""
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["pirms dienām", "pēc gadiem"])
def test_a_plural_unit_without_a_count_is_not_an_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_a_month_name_inside_a_word_is_not_a_month():
    nomatch("maijsvētki")


PAIRS = [
    ("šodien", "today"), ("rīt", "tomorrow"), ("vakar", "yesterday"),
    ("parīt", "overmorrow"), ("aizvakar", "ereyesterday"),
    ("pēc 1 dienas", "in 1 day"), ("pēc 3 dienām", "in 3 days"),
    ("pēc 2 nedēļām", "in 2 weeks"), ("pēc 2 mēnešiem", "in 2 months"),
    ("pēc 5 gadiem", "in 5 years"), ("pēc 15 minūtēm", "in 15 minutes"),
    ("pēc 10 stundām", "in 10 hours"), ("pirms 3 dienām", "3 days ago"),
    ("pirms 11 gadiem", "11 years ago"), ("pirms 21 gada", "21 years ago"),
    ("nākamajā piektdienā", "next friday"),
    ("nākamajā pirmdienā", "next monday"),
    ("pagājušajā otrdienā", "last tuesday"),
    ("15:30", "15:30"), ("09:30", "09:30"), ("00:00", "00:00"),
    ("pusdienlaikā", "noon"), ("pusnaktī", "midnight"),
    ("2019", "2019"), ("1918", "1918"), ("2017-06-30", "2017-06-30"),
    ("vasara 2020", "summer 2020"), ("nākamā ziema", "next winter"),
    ("5. jūlijā", "july 5"),
    ("2020. gada 25. decembris", "25 december 2020"),
    ("20. gadsimts", "the 20th century"),
]


@pytest.mark.parametrize("lv_text,en_text", PAIRS)
def test_span_parity(lv_text, en_text):
    lv = extract_timespan(lv_text, "lv", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert lv is not None, f"lv {lv_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert lv[0].start == en[0].start and lv[0].end == en[0].end, (lv_text, en_text)
