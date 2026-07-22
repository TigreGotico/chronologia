"""Shared semantic-parity block: an Occitan phrase must resolve to the *same*
span as its English staple.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR


# (occitan, english) translation pairs that must land on the identical span
PAIRS = [
    ("uèi", "today"),
    ("deman", "tomorrow"),
    ("ièr", "yesterday"),
    ("passat deman", "overmorrow"),
    ("abans ièr", "ereyesterday"),
    ("dins 3 jorns", "in 3 days"),
    ("dins 5 jorns", "in 5 days"),
    ("dins 2 setmanas", "in 2 weeks"),
    ("dins 1 jorn", "in 1 day"),
    ("dins 2 meses", "in 2 months"),
    ("dins 5 ans", "in 5 years"),
    ("dins 3 oras", "in 3 hours"),
    ("dins 15 minutas", "in 15 minutes"),
    ("divendres que ven", "next friday"),
    ("diluns que ven", "next monday"),
    ("15:30", "15:30"),
    ("09:30", "09:30"),
    ("00:00", "00:00"),
    ("a miègjorn", "noon"),
    ("a mièjanuèch", "midnight"),
    ("2019", "2019"),
    ("1989", "1989"),
    ("2017-06-30", "2017-06-30"),
    ("de junh a agost", "from june to august"),
    ("de genièr a març", "from january to march"),
    ("entre junh e setembre", "between june and september"),
    ("estiu 2020", "summer 2020"),
    ("44 abans jèsus-crist", "44 bc"),
    ('la setmana que ven', 'next week'),
    ("l'an passat", 'last year'),
    ('aquesta dimenjada', 'this weekend'),
]


@pytest.mark.parametrize("oc_text,en_text", PAIRS)
def test_span_parity(oc_text, en_text):
    oc = extract_timespan(oc_text, "oc", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert oc is not None, f"oc {oc_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert oc[0].start == en[0].start, (oc_text, en_text)
    assert oc[0].end == en[0].end, (oc_text, en_text)
