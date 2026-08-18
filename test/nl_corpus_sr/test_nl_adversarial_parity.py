"""Semantic-parity block: sr/en phrase pairs that must resolve to the exact
same span, in the shared discovery convention (see ``test_language_parity``).
"""
import pytest

from ._corpus import ANCHOR

from chronologia import extract_timespan

PAIRS = [
    ("danas", "today"),
    ("sutra", "tomorrow"),
    ("juče", "yesterday"),
    ("prekjuče", "the day before yesterday"),
    ("prekosutra", "the day after tomorrow"),
    ("za 3 dana", "in 3 days"),
    ("pre 3 dana", "3 days ago"),
    ("za 2 sedmice", "in 2 weeks"),
    ("za 5 godina", "in 5 years"),
    ("sledeći petak", "next friday"),
    ("prošli utorak", "last tuesday"),
    ("15:30", "15:30"),
    ("00:00", "00:00"),
    ("podne", "noon"),
    ("ponoć", "midnight"),
    ("2019", "2019"),
    ("2017-06-30", "2017-06-30"),
    ("leto 2020", "summer 2020"),
    ("sledeća zima", "next winter"),
    ("vikend", "weekend"),
    ("5. maj 2020.", "may 5 2020"),
    ("januar", "january"),
    ("ove godine", "this year"),
    ("sledeće godine", "next year"),
    ("prošle godine", "last year"),
]


@pytest.mark.parametrize("sr_text,en_text", PAIRS)
def test_span_parity(sr_text, en_text):
    sr = extract_timespan(sr_text, "sr", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert sr is not None and en is not None, (sr_text, en_text)
    assert sr[0].start == en[0].start and sr[0].end == en[0].end, \
        (sr_text, en_text)
