"""Semantic-parity block: a German phrase must resolve to the SAME span as
its English staple (same anchor).  This is the cross-language contract --
the engine core is shared, so equivalent phrasings must land identically.

Clock TIMES that diverge by the half-trap ("halb neun" != "half nine") are
deliberately excluded here and asserted in test_de_clock.py; the clock
entries below use phrasings that are invariant across the two languages
(digit times, landmarks, explicit quarter-past).
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

#: (english, german) -- must produce identical spans.
PAIRS = [
    ("today", "heute"),
    ("yesterday", "gestern"),
    ("tomorrow", "morgen"),
    ("overmorrow", "übermorgen"),
    ("three days ago", "vor drei tagen"),
    ("in three days", "in drei tagen"),
    ("two weeks ago", "vor zwei wochen"),
    ("in ten years", "in zehn jahren"),
    ("next monday", "nächsten montag"),
    ("last friday", "letzten freitag"),
    ("october 2020", "oktober 2020"),
    ("march 1999", "märz 1999"),
    ("the year 1969", "das jahr 1969"),
    ("1969", "1969"),
    ("44 bc", "44 v. chr."),
    ("753 bc", "753 v. chr."),
    ("2024 ad", "2024 n. chr."),
    ("66 million years ago", "vor 66 millionen jahren"),
    ("summer 2020", "sommer 2020"),
    ("next summer", "nächster sommer"),
    ("spring 2021", "frühling 2021"),
    ("the third century", "das dritte jahrhundert"),
    ("the 21st century", "das 21. jahrhundert"),
    ("the first half of 2020", "die erste hälfte von 2020"),
    ("2019-03-15", "2019-03-15"),
    ("15:30", "15:30"),
    ("midnight", "mitternacht"),
    ("noon", "mittag"),
    ("quarter past three", "viertel nach drei"),
    ("from june 5th to june 12th", "von 5. juni bis 12. juni"),
]


@pytest.mark.parametrize("en_text,de_text", PAIRS)
def test_parity(en_text, de_text):
    en = extract_timespan(en_text, "en", ANCHOR)
    de = extract_timespan(de_text, "de", ANCHOR)
    assert en is not None, f"english staple {en_text!r} did not parse"
    assert de is not None, f"german {de_text!r} did not parse"
    assert de[0].start == en[0].start, f"{de_text!r} vs {en_text!r} start"
    assert de[0].end == en[0].end, f"{de_text!r} vs {en_text!r} end"


def test_parity_block_size():
    assert len(PAIRS) >= 30
