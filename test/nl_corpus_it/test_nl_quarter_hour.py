# -*- coding: utf-8 -*-
"""Quarter-hour offsets in Italian: "tra tre quarti d'ora".

Expected values are hand arithmetic from the anchor 2017-06-27 13:04.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text,minutes", [
    ("tra tre quarti d'ora", 45),
    ("fra tre quarti d'ora", 45),
    ("tra un quarto d'ora", 15),
    ("fra un quarto d'ora", 15),
])
def test_quarter_hour_offset(text, minutes):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(ANCHOR + timedelta(minutes=minutes))
    assert r.remainder == ""
