# -*- coding: utf-8 -*-
"""Kabyle dayparts + weekend. Surfaces attested by native speaker
athmanemokraoui (TigreGotico/chronologia#265). Anchor Tue 2017-06-27."""
from datetime import datetime
import pytest
from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)  # Tuesday


def _span(text):
    r = extract_timespan(text, "kab", ANCHOR)
    assert r is not None and r[0] is not None, f"{text!r} did not parse"
    assert r[1] == "", f"{text!r} left remainder {r[1]!r}"
    return r[0]


@pytest.mark.parametrize("text,h0,h1", [
    ("ass-a ṣṣbeḥ", 6, 12),    # this morning
    ("ṣṣbeḥ-a", 6, 12),
    ("tameddit", 18, 21),       # evening
])
def test_daypart(text, h0, h1):
    s = _span(text)
    assert (s.start_datetime.hour, s.end_datetime.hour) == (h0, h1)


def test_weekend_is_friday_saturday():
    # Kabyle weekend = Fri-Sat; from Tue 2017-06-27 the coming weekend
    # starts Fri 2017-06-30.
    s = _span("taggara n ssmana")
    assert s.start_datetime.date().isoformat() == "2017-06-30"   # Friday
    assert (s.end_datetime - s.start_datetime).days == 2
