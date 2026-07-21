"""Shared semantic-parity block: a Slovak phrase must resolve to the *same*
span as its English staple.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR


PAIRS = [
    ("dnes", "today"),
    ("zajtra", "tomorrow"),
    ("včera", "yesterday"),
    ("pozajtra", "overmorrow"),
    ("predvčerom", "ereyesterday"),
    ("za 3 dni", "in 3 days"),
    ("za 5 dní", "in 5 days"),
    ("za 2 týždne", "in 2 weeks"),
    ("za 1 deň", "in 1 day"),
    ("za 2 mesiace", "in 2 months"),
    ("za 5 rokov", "in 5 years"),
    ("cez 3 hodiny", "in 3 hours"),
    ("o 15 minút", "in 15 minutes"),
    ("budúci piatok", "next friday"),
    ("budúci pondelok", "next monday"),
    ("minulý utorok", "last tuesday"),
    ("15:30", "15:30"),
    ("09:30", "09:30"),
    ("00:00", "00:00"),
    ("poludnie", "noon"),
    ("polnoc", "midnight"),
    ("2019", "2019"),
    ("1989", "1989"),
    ("2017-06-30", "2017-06-30"),
    ("od júna do augusta", "from june to august"),
    ("od januára do marca", "from january to march"),
    ("medzi júnom a septembrom", "between june and september"),
    ("leto 2020", "summer 2020"),
    ("budúca zima", "next winter"),
]


@pytest.mark.parametrize("sk_text,en_text", PAIRS)
def test_span_parity(sk_text, en_text):
    sk = extract_timespan(sk_text, "sk", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert sk is not None, f"sk {sk_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert sk[0].start == en[0].start, (sk_text, en_text)
    assert sk[0].end == en[0].end, (sk_text, en_text)
