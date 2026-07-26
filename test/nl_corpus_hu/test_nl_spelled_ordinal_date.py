# -*- coding: utf-8 -*-
"""Hungarian spelled-ordinal day-of-month.  Hungarian is month-first
("április tizenötödik" = the fifteenth of April).  The single-token ordinal
(which the cardinal back-end does not read) must fold to the exact day, not
strand and leave the whole month.  ``pronounce_ordinal_hu`` emits every 1..31
as one word, so the whole range folds.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start


@pytest.mark.parametrize("ordinal,d", [
    ("első", 1),
    ("ötödik", 5),
    ("tizenegyedik", 11),
    ("tizenötödik", 15),
    ("huszonegyedik", 21),
    ("huszonharmadik", 23),
    ("harmincadik", 30),
])
def test_spelled_ordinal_of_april(ordinal, d):
    assert start(f"április {ordinal}") == ad(datetime(2018, 4, d))


def test_spelled_thirty_first_of_march():
    assert start("március harmincegyedik") == ad(datetime(2018, 3, 31))
