# -*- coding: utf-8 -*-
"""Estonian spelled-ordinal day-of-month ("viieteistkümnes aprill" = the
fifteenth of April).  The single-token ordinal the cardinal back-end does not
read must fold to the exact day.  ``pronounce_ordinal_et`` emits 1..20 and 30
as one word; the compound tens 21..29/31 are TWO words ("kahekümne esimene"),
which the single-token ordinal pre-pass cannot fold -- those remain a
documented deferral, so this corpus covers the single-word range.
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
