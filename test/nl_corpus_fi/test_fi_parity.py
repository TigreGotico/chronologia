"""Semantic-parity block: a Finnish phrase must resolve to the SAME span as
its English staple (same anchor).  The half-to clock ("puoli yhdeksän" !=
"half nine") is asserted in test_fi_clock.py, not here.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

#: (english, finnish) -- must produce identical spans.
PAIRS = [
    ("today", "tänään"),
    ("yesterday", "eilen"),
    ("tomorrow", "huomenna"),
    ("overmorrow", "ylihuomenna"),
    ("in three days", "kolmen päivän kuluttua"),
    ("three days ago", "kolme päivää sitten"),
    ("in two weeks", "kahden viikon kuluttua"),
    ("two weeks ago", "kaksi viikkoa sitten"),
    ("in ten years", "kymmenen vuoden kuluttua"),
    ("five months ago", "viisi kuukautta sitten"),
    ("in one week", "viikon kuluttua"),
    ("30 minutes ago", "30 minuuttia sitten"),
    ("next monday", "ensi maanantaina"),
    ("last friday", "viime perjantaina"),
    ("2020-06-05", "5. kesäkuuta 2020"),
    ("1969-07-20", "20. heinäkuuta 1969"),
    ("the year 1969", "1969"),
    ("1969", "1969"),
    ("2000", "2000"),
    ("44 bc", "44 ekr."),
    ("753 bc", "753 ekr."),
    ("2024 ad", "2024 jkr."),
    ("66 million years ago", "66 miljoonaa vuotta sitten"),
    ("summer 2020", "kesä 2020"),
    ("spring 2021", "kevät 2021"),
    ("winter 2020", "talvi 2020"),
    ("2019-03-15", "2019-03-15"),
    ("15:30", "15:30"),
    ("midnight", "keskiyö"),
    ("noon", "keskipäivä"),
]


@pytest.mark.parametrize("en_text,fi_text", PAIRS)
def test_parity(en_text, fi_text):
    en = extract_timespan(en_text, "en", ANCHOR)
    fi = extract_timespan(fi_text, "fi", ANCHOR)
    assert en is not None, f"english staple {en_text!r} did not parse"
    assert fi is not None, f"finnish {fi_text!r} did not parse"
    assert fi[0].start == en[0].start, f"{fi_text!r} vs {en_text!r} start"
    assert fi[0].end == en[0].end, f"{fi_text!r} vs {en_text!r} end"


def test_parity_block_size():
    assert len(PAIRS) >= 25
