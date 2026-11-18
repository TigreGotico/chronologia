# -*- coding: utf-8 -*-
"""The half hour written with "nnefṣ" (Arabic "nisf", half).

The Amazigh fraction list of ovos-number-parser (numbers_kab) holds "nnefṣ"
as the half, and the ovos-skill-alerts locale files write "ɣef sebɛa u nnefṣ"
for half past seven.  The word is the half beside "azgen" and "wezgen", so the
hour keeps its half.

Anchor 2017-06-27 13:04.  A lone hour 1 to 12 takes the next twelve-hour
reading (ruling 17), so seven is 19:00 the same day, and a clock that names
the evening ("n tmeddit") is that evening.  The expected instants are worked
out from the anchor by hand.
"""
from datetime import datetime

import pytest

from ._corpus import parse

A = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("text,want,rest", [
    ("sbedd-iyi-d alarme ɣef sebɛa u nnefṣ", (2017, 6, 27, 19, 30),
     "sbedd-iyi-d alarme"),
    ("ɣef ssebɛa u nnefṣ", (2017, 6, 27, 19, 30), ""),
    ("ɣef sebɛa d wezgen", (2017, 6, 27, 19, 30), ""),
    ("ɣef tmanya u nnefṣ n tmeddit", (2017, 6, 27, 20, 30), ""),
])
def test_half_past_the_hour(text, want, rest):
    r = parse(text, A)
    assert r is not None, "%r did not parse" % text
    s = r[0].start
    assert (s.year, s.month, s.day, s.hour, s.minute) == want
    assert r[1] == rest
