"""Shared semantic-parity block: an Italian phrase must resolve to the *same*
span as its English staple.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR


# (italian, english) translation pairs that must land on the identical span
PAIRS = [
    ("oggi", "today"),
    ("domani", "tomorrow"),
    ("ieri", "yesterday"),
    ("dopodomani", "overmorrow"),
    ("altroieri", "ereyesterday"),
    ("tra 3 giorni", "in 3 days"),
    ("tra 5 giorni", "in 5 days"),
    ("tra 2 settimane", "in 2 weeks"),
    ("tra 1 giorno", "in 1 day"),
    ("tra 2 mesi", "in 2 months"),
    ("tra 5 anni", "in 5 years"),
    ("tra 3 ore", "in 3 hours"),
    ("tra 15 minuti", "in 15 minutes"),
    ("venerdì prossimo", "next friday"),
    ("lunedì prossimo", "next monday"),
    ("martedì scorso", "last tuesday"),
    ("questo giovedì", "this thursday"),
    ("15:30", "15:30"),
    ("09:30", "09:30"),
    ("00:00", "00:00"),
    ("mezzogiorno", "noon"),
    ("mezzanotte", "midnight"),
    ("2019", "2019"),
    ("1989", "1989"),
    ("2017-06-30", "2017-06-30"),
    ("da giugno ad agosto", "from june to august"),
    ("da gennaio a marzo", "from january to march"),
    ("tra giugno e settembre", "between june and september"),
    ("estate 2020", "summer 2020"),
    ("44 avanti cristo", "44 bc"),
    ('la settimana prossima', 'next week'),
    ('lo scorso anno', 'last year'),
    ('questo fine settimana', 'this weekend'),
]


@pytest.mark.parametrize("it_text,en_text", PAIRS)
def test_span_parity(it_text, en_text):
    it = extract_timespan(it_text, "it", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert it is not None, f"it {it_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert it[0].start == en[0].start, (it_text, en_text)
    assert it[0].end == en[0].end, (it_text, en_text)
