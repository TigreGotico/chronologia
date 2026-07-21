"""Shared semantic-parity block: a Czech phrase must resolve to the *same*
span as its English staple.  This ties the Czech locale to the same
hand-checked reference spans the English corpus asserts, rather than to the
engine's own output.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR


# (czech, english) translation pairs that must land on the identical span
PAIRS = [
    ("dnes", "today"),
    ("zítra", "tomorrow"),
    ("včera", "yesterday"),
    ("pozítří", "overmorrow"),
    ("předevčírem", "ereyesterday"),
    ("za 3 dny", "in 3 days"),
    ("za 5 dní", "in 5 days"),
    ("za 2 týdny", "in 2 weeks"),
    ("za 1 den", "in 1 day"),
    ("za 2 měsíce", "in 2 months"),
    ("za 5 let", "in 5 years"),
    ("za 3 hodiny", "in 3 hours"),
    ("za 15 minut", "in 15 minutes"),
    ("příští pátek", "next friday"),
    ("příští pondělí", "next monday"),
    ("minulé úterý", "last tuesday"),
    ("tento čtvrtek", "this thursday"),
    ("15:30", "15:30"),
    ("09:30", "09:30"),
    ("00:00", "00:00"),
    ("poledne", "noon"),
    ("půlnoc", "midnight"),
    ("2019", "2019"),
    ("1989", "1989"),
    ("2017-06-30", "2017-06-30"),
    ("od června do srpna", "from june to august"),
    ("od ledna do března", "from january to march"),
    ("mezi červnem a zářím", "between june and september"),
    ("léto 2020", "summer 2020"),
    ("příští zima", "next winter"),
]


@pytest.mark.parametrize("cs_text,en_text", PAIRS)
def test_span_parity(cs_text, en_text):
    cs = extract_timespan(cs_text, "cs", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert cs is not None, f"cs {cs_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert cs[0].start == en[0].start, (cs_text, en_text)
    assert cs[0].end == en[0].end, (cs_text, en_text)
