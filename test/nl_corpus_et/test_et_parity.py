"""Semantic-parity block: an Estonian phrase must resolve to the SAME span as
its English staple (same anchor).  The half-to clock ("pool üheksa" != "half
nine") is asserted in test_et_clock.py, not here.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

#: (english, estonian) -- must produce identical spans.
PAIRS = [
    ("today", "täna"),
    ("yesterday", "eile"),
    ("tomorrow", "homme"),
    ("overmorrow", "ülehomme"),
    ("in three days", "kolme päeva pärast"),
    ("three days ago", "kolm päeva tagasi"),
    ("in two weeks", "kahe nädala pärast"),
    ("two weeks ago", "kaks nädalat tagasi"),
    ("in ten years", "kümne aasta pärast"),
    ("five months ago", "viis kuud tagasi"),
    ("in one week", "nädala pärast"),
    ("30 minutes ago", "30 minutit tagasi"),
    ("next monday", "järgmisel esmaspäeval"),
    ("last friday", "eelmisel reedel"),
    ("2020-06-05", "5. juuni 2020"),
    ("1969-07-20", "20. juuli 1969"),
    ("the year 1969", "1969"),
    ("1969", "1969"),
    ("2000", "2000"),
    ("44 bc", "44 ekr"),
    ("753 bc", "753 ekr"),
    ("2024 ad", "2024 pkr"),
    ("66 million years ago", "66 miljonit aastat tagasi"),
    ("summer 2020", "suvi 2020"),
    ("spring 2021", "kevad 2021"),
    ("winter 2020", "talv 2020"),
    ("2019-03-15", "2019-03-15"),
    ("15:30", "15:30"),
    ("midnight", "kesköö"),
    ("noon", "keskpäev"),
]


@pytest.mark.parametrize("en_text,et_text", PAIRS)
def test_parity(en_text, et_text):
    en = extract_timespan(en_text, "en", ANCHOR)
    et = extract_timespan(et_text, "et", ANCHOR)
    assert en is not None, f"english staple {en_text!r} did not parse"
    assert et is not None, f"estonian {et_text!r} did not parse"
    assert et[0].start == en[0].start, f"{et_text!r} vs {en_text!r} start"
    assert et[0].end == en[0].end, f"{et_text!r} vs {en_text!r} end"


def test_parity_block_size():
    assert len(PAIRS) >= 25
