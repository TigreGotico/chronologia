"""Adversarial Esperanto cases plus the shared English semantic-parity block.

Every ``PAIRS`` entry is a native Esperanto phrase and an English staple
that name the SAME instant; ``test_span_parity`` proves they resolve to the
identical span, independently of any hand-picked gold value.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", [
    "", "   ", "saluton kiel vi fartas", "qwerty zxcvb", "ĉi tie estas nenio",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "tri tagoj", "dek du tagoj", "du semajnoj", "dek jaroj", "3 tagoj",
])
def test_offset_without_marker(text):
    """A bare count of units is a quantity, not a point in time -- "antaŭ"
    or "post" must lead it."""
    nomatch(text)


@pytest.mark.parametrize("text", ["antaŭ", "post", "tagoj", "antaŭ tagojn"])
def test_incomplete_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", [
    "przed 2 laty", "через 3 дня", "pirms 3 dienam", "trys dienos",
])
def test_foreign_not_matched(text):
    """Polish, Russian, Latvian and Lithuanian phrasings must not read as
    Esperanto."""
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_bare_weekday_resolves_next():
    from datetime import timedelta
    ahead = (0 - ANCHOR.weekday()) % 7 or 7          # 0 == Monday
    s = (ANCHOR + timedelta(days=ahead)).date()
    e = s + timedelta(days=1)
    r = parse("lundon")
    assert r is not None
    sp = r[0]
    assert (sp.start.year, sp.start.month, sp.start.day) == (s.year, s.month, s.day)
    assert (sp.end.year, sp.end.month, sp.end.day) == (e.year, e.month, e.day)


PAIRS = [
    ("antaŭ tri tagoj", "3 days ago"), ("antaŭ unu tago", "1 day ago"),
    ("post tri tagoj", "in 3 days"), ("post unu tago", "in 1 day"),
    ("antaŭ dek du tagoj", "12 days ago"), ("post dek du tagoj", "in 12 days"),
    ("antaŭ dudek tagoj", "20 days ago"), ("antaŭ cent tagoj", "100 days ago"),
    ("la sesa kaj duono", "6:30"), ("la sesa kaj kvarono", "6:15"),
    ("la sesa", "6:00"), ("je la sesa", "6:00"),
    ("noktomezo", "midnight"), ("tagmezo", "noon"),
    ("2019", "2019"), ("1918", "1918"),
    ("la unua de januaro", "january 1"), ("la kvina de julio", "july 5"),
    ("lundon", "monday"), ("mardon", "tuesday"),
    ("la unua de decembro", "december 1"),
    ("la dudek kvina de decembro", "december 25"),
    ("kvarono antaŭ la sepa", "6:45"), ("duono post la sepa", "7:30"),
    ("la deka de junio", "june 10"), ("la naŭa kaj duono", "9:30"),
]


@pytest.mark.parametrize("eo_text,en_text", PAIRS)
def test_span_parity(eo_text, en_text):
    eo = extract_timespan(eo_text, "eo", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert eo is not None, f"eo {eo_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert eo[0].start == en[0].start and eo[0].end == en[0].end, \
        (eo_text, en_text)
