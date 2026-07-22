"""Shared semantic-parity block: a Romanian phrase must resolve to the *same*
span as its English staple.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR


# (romanian, english) translation pairs that must land on the identical span
PAIRS = [
    ("azi", "today"),
    ("mâine", "tomorrow"),
    ("ieri", "yesterday"),
    ("poimâine", "overmorrow"),
    ("alaltăieri", "ereyesterday"),
    ("peste 3 zile", "in 3 days"),
    ("peste 5 zile", "in 5 days"),
    ("peste 2 săptămâni", "in 2 weeks"),
    ("peste 1 zi", "in 1 day"),
    ("peste 2 luni", "in 2 months"),
    ("peste 5 ani", "in 5 years"),
    ("peste 3 ore", "in 3 hours"),
    ("peste 15 minute", "in 15 minutes"),
    ("vineri viitoare", "next friday"),
    ("luni viitoare", "next monday"),
    ("marți trecută", "last tuesday"),
    ("15:30", "15:30"),
    ("09:30", "09:30"),
    ("00:00", "00:00"),
    ("2019", "2019"),
    ("1989", "1989"),
    ("2017-06-30", "2017-06-30"),
    ("la amiază", "noon"),
    ("din iunie până în august", "from june to august"),
    ("din ianuarie până în martie", "from january to march"),
    ("între iunie și septembrie", "between june and september"),
    ("vara 2020", "summer 2020"),
    ("44 î.hr.", "44 bc"),
    ('săptămâna viitoare', 'next week'),
    ('anul trecut', 'last year'),
    ('acest weekend', 'this weekend'),
]


@pytest.mark.parametrize("ro_text,en_text", PAIRS)
def test_span_parity(ro_text, en_text):
    ro = extract_timespan(ro_text, "ro", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert ro is not None, f"ro {ro_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert ro[0].start == en[0].start, (ro_text, en_text)
    assert ro[0].end == en[0].end, (ro_text, en_text)
