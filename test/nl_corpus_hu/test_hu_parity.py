"""Semantic-parity block: a Hungarian phrase must resolve to the SAME span as
its English staple (same anchor).  The engine core is shared, so equivalent
phrasings must land identically.  The half-to clock ("fél kilenc" != "half
nine") is asserted in test_hu_clock.py, not here.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

#: (english, hungarian) -- must produce identical spans.
PAIRS = [
    ("today", "ma"),
    ("yesterday", "tegnap"),
    ("tomorrow", "holnap"),
    ("overmorrow", "holnapután"),
    ("in three days", "3 nap múlva"),
    ("three days ago", "három nappal ezelőtt"),
    ("in two weeks", "két hét múlva"),
    ("two weeks ago", "két héttel ezelőtt"),
    ("in ten years", "tíz év múlva"),
    ("five months ago", "5 hónappal ezelőtt"),
    ("30 minutes ago", "30 perccel ezelőtt"),
    ("in 15 minutes", "15 perc múlva"),
    ("next monday", "jövő hétfőn"),
    ("last friday", "múlt pénteken"),
    ("2020-06-05", "2020. június 5."),
    ("march 1999", "1999. március"),
    ("the year 1969", "1969"),
    ("1969", "1969"),
    ("2000", "2000"),
    ("44 bc", "44 i. e."),
    ("753 bc", "753 i. e."),
    ("2024 ad", "2024 i. sz."),
    ("66 million years ago", "66 millió évvel ezelőtt"),
    ("summer 2020", "nyár 2020"),
    ("spring 2021", "tavasz 2021"),
    ("winter 2020", "tél 2020"),
    ("2019-03-15", "2019-03-15"),
    ("15:30", "15:30"),
    ("midnight", "éjfél"),
    ("noon", "délben"),
]


@pytest.mark.parametrize("en_text,hu_text", PAIRS)
def test_parity(en_text, hu_text):
    en = extract_timespan(en_text, "en", ANCHOR)
    hu = extract_timespan(hu_text, "hu", ANCHOR)
    assert en is not None, f"english staple {en_text!r} did not parse"
    assert hu is not None, f"hungarian {hu_text!r} did not parse"
    assert hu[0].start == en[0].start, f"{hu_text!r} vs {en_text!r} start"
    assert hu[0].end == en[0].end, f"{hu_text!r} vs {en_text!r} end"


def test_parity_block_size():
    assert len(PAIRS) >= 25
