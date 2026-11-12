# -*- coding: utf-8 -*-
"""A clock followed by "e" and a minute count is not that clock, gl.

"ás 20h e 45" read 20:00 and left "e 45" in the remainder: a time 45
minutes off with no sign of it but the leftover.  The library has no reading
for the mixed form, so it refuses rather than answer half of it.  A written
hour on its own and the spelled "ás 20 e 45" keep their readings.  Anchor
2017-06-27 13:04.
"""
import pytest

from ._corpus import nomatch, span


@pytest.mark.parametrize("text", [
    "ás 20h e 45",
    "ás 20h e 45m",
    "ás 20h e 45m gzqx 99h",
    "ás 20:00 e 45",
])
def test_half_read_hour_letter_refuses(text):
    nomatch(text)


@pytest.mark.parametrize("text,hour,minute", [
    ("ás 20h", 20, 0),
    ("ás 20 e 45", 20, 45),
    ("ás 20h45", 20, 45),
])
def test_complete_clock_still_reads(text, hour, minute):
    s = span(text)
    assert (s.start.day, s.start.hour, s.start.minute) == (27, hour, minute)
