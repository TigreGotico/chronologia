# -*- coding: utf-8 -*-
"""Estonian spelled-ordinal day-of-month ("viieteistkümnes aprill" = the
fifteenth of April).  The ordinal must fold to the exact day.  numtag reads 1..20 and 30 as one
word, which this corpus covers; the compound tens 21..29/31 are two words
("kahekümne esimene") that numtag reads as one ordinal, covered in
test_et_adessive_ordinal_day.py.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start


@pytest.mark.parametrize("ordinal,d", [
    ("esimene", 1),
    ("viies", 5),
    ("üheteistkümnes", 11),
    ("viieteistkümnes", 15),
    ("kaheksateistkümnes", 18),
    ("kahekümnes", 20),
    ("kolmekümnes", 30),
])
def test_spelled_ordinal_of_april(ordinal, d):
    assert start(f"{ordinal} aprill") == ad(datetime(2018, 4, d))
