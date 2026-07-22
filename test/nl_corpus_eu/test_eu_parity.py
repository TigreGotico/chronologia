"""Semantic-parity block: a Basque phrase must resolve to the SAME span as
its English staple (same anchor).  The engine core is shared, so equivalent
phrasings must land identically.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

#: (english, basque) -- must produce identical spans.
PAIRS = [
    # rel_period / weekend / bare-weekday rollout
    ('next week', 'datorren astea'),
    ('this weekend', 'asteburua'),
    ('friday', 'ostirala'),
    ("today", "gaur"),
    ("yesterday", "atzo"),
    ("tomorrow", "bihar"),
    ("overmorrow", "etzi"),
    ("in three days", "3 egun barru"),
    ("three days ago", "duela 3 egun"),
    ("in two weeks", "bi aste barru"),
    ("two weeks ago", "duela bi aste"),
    ("in ten years", "10 urte barru"),
    ("five months ago", "duela 5 hilabete"),
    ("in one week", "aste bat barru"),
    ("30 minutes ago", "duela 30 minutu"),
    ("next monday", "datorren astelehena"),
    ("last friday", "aurreko ostirala"),
    ("2020-06-05", "2020ko ekainaren 5ean"),
    ("1969-07-20", "1969ko uztailaren 20an"),
    ("the year 1969", "1969"),
    ("1969", "1969"),
    ("2000", "2000"),
    ("44 bc", "44 k.a."),
    ("753 bc", "753 k.a."),
    ("2024 ad", "2024 k.o."),
    ("66 million years ago", "duela 66 milioi urte"),
    ("summer 2020", "uda 2020"),
    ("spring 2021", "udaberria 2021"),
    ("winter 2020", "negua 2020"),
    ("2019-03-15", "2019-03-15"),
    ("15:30", "15:30"),
    ("midnight", "gauerdia"),
    ("noon", "eguerdia"),
]


@pytest.mark.parametrize("en_text,eu_text", PAIRS)
def test_parity(en_text, eu_text):
    en = extract_timespan(en_text, "en", ANCHOR)
    eu = extract_timespan(eu_text, "eu", ANCHOR)
    assert en is not None, f"english staple {en_text!r} did not parse"
    assert eu is not None, f"basque {eu_text!r} did not parse"
    assert eu[0].start == en[0].start, f"{eu_text!r} vs {en_text!r} start"
    assert eu[0].end == en[0].end, f"{eu_text!r} vs {en_text!r} end"


def test_parity_block_size():
    assert len(PAIRS) >= 25
