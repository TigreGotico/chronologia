"""Marwari (mwr) corpus.

Gold comes from ``datetime`` arithmetic on the anchor, never from the parser.
Every surface is cited in the ``.voc`` file that ships it.  काल and परसूं name
a day in either direction (issue #1484), so the bare forms are refused.
Spelled numbers wait on the numtag Marwari lexicon (TigreGotico/numtag#384).
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a Tuesday


def start(text):
    r = extract_timespan(text, "mwr", ANCHOR)
    assert r is not None, text
    s = r.span.start
    return datetime(s.year, s.month, s.day, s.hour, s.minute)


MIDNIGHT = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text, gold", [
    ("आज", MIDNIGHT),
    ("म्हैं आज बजार जासूं", MIDNIGHT),
    ("3 दिनां में", ANCHOR + timedelta(days=3)),
    ("३ दिनां में", ANCHOR + timedelta(days=3)),
    ("2 दिन पछै", ANCHOR + timedelta(days=2)),
    ("१० दिनां पछै", ANCHOR + timedelta(days=10)),
    ("2 बरस पछै", ANCHOR.replace(year=2019)),
    ("5 जुलाई", datetime(2017, 7, 5)),
    ("५ जुलाई २०१८", datetime(2018, 7, 5)),
    ("20 सितम्बर", datetime(2017, 9, 20)),
    ("3 फरवरी", datetime(2018, 2, 3)),
    ("15:30", ANCHOR.replace(hour=15, minute=30)),
    ("१५:३०", ANCHOR.replace(hour=15, minute=30)),
    ("4:30 सांम", ANCHOR.replace(hour=16, minute=30)),
    ("9:15 सबेरे", datetime(2017, 6, 28, 9, 15)),
])
def test_reads(text, gold):
    assert start(text) == gold


@pytest.mark.parametrize("text", [
    "काल", "परसूं", "परसू",
    "थोडा दिनां में ई पीजारी बरसां बढ़ हुयग्यौ",  # Bahal 1964, no number
    "ओ वो ही आदमी है जको काल मिलियो हो",  # Swami Narottamdas, two-way काल
    "म्हारी दादीसा मेळा सूं चूड़्यां लेय'र आई",
    "ब्याव में लुगायां मंगळ गीत गावै",
])
def test_refuses(text):
    assert extract_timespan(text, "mwr", ANCHOR) is None


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="spelled numbers wait on TigreGotico/numtag#384")
@pytest.mark.parametrize("text, gold", [
    ("तीन दिनां में", ANCHOR + timedelta(days=3)),
    ("दो दिन पछै", ANCHOR + timedelta(days=2)),
])
def test_spelled_offset_waits_on_numtag(text, gold):
    assert start(text) == gold


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="no source in the library attests the clock word बजे")
def test_digit_hour_with_baje_waits_on_a_source():
    assert start("4 बजे") == ANCHOR.replace(hour=16, minute=0)
