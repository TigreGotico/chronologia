"""Adversarial Polish cases plus the shared English semantic-parity block."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, parse, nomatch


@pytest.mark.parametrize("text", [
    "", "   ", "cześć jak się masz", "qwerty zxcvb", "brak daty tutaj",
])
def test_junk_is_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "pięć dni", "dwa tygodnie", "trzy miesiące", "dziesięć lat",
])
def test_offset_without_marker(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["za tygodnie", "2 temu"])
def test_incomplete_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


# Czech / Russian phrases must not parse as Polish
@pytest.mark.parametrize("text", [
    "před 2 lety", "через 3 дня", "vidimo se za tri sata", "sutra",
])
def test_foreign_not_matched(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_seconds_offset_gap():
    nomatch("za 45 sekund")


def test_bare_weekday_resolves_next():
    # a bare weekday names its next strictly-future occurrence, a day-wide span
    from datetime import timedelta
    from ._corpus import span
    ahead = (4 - ANCHOR.weekday()) % 7 or 7          # 4 == Friday (piątek)
    s = (ANCHOR + timedelta(days=ahead)).date()
    e = s + timedelta(days=1)
    sp = span("piątek")
    assert (sp.start.year, sp.start.month, sp.start.day) == (s.year, s.month, s.day)
    assert (sp.end.year, sp.end.month, sp.end.day) == (e.year, e.month, e.day)


PAIRS = [
    ("dziś", "today"), ("jutro", "tomorrow"), ("wczoraj", "yesterday"),
    ("pojutrze", "overmorrow"), ("przedwczoraj", "ereyesterday"),
    ("za 3 dni", "in 3 days"), ("za 2 tygodnie", "in 2 weeks"),
    ("za 1 dzień", "in 1 day"), ("za 2 miesiące", "in 2 months"),
    ("za 5 lat", "in 5 years"), ("za 15 minut", "in 15 minutes"),
    ("przyszły piątek", "next friday"), ("przyszły poniedziałek", "next monday"),
    ("zeszły wtorek", "last tuesday"), ("15:30", "15:30"), ("09:30", "09:30"),
    ("00:00", "00:00"), ("południe", "noon"), ("północ", "midnight"),
    ("2019", "2019"), ("1918", "1918"), ("2017-06-30", "2017-06-30"),
    ("od czerwca do sierpnia", "from june to august"),
    ("od stycznia do marca", "from january to march"),
    ("między czerwcem a wrześniem", "between june and september"),
    ("lato 2020", "summer 2020"), ("przyszła zima", "next winter"),
]


@pytest.mark.parametrize("pl_text,en_text", PAIRS)
def test_span_parity(pl_text, en_text):
    pl = extract_timespan(pl_text, "pl", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert pl is not None, f"pl {pl_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert pl[0].start == en[0].start and pl[0].end == en[0].end, (pl_text, en_text)
