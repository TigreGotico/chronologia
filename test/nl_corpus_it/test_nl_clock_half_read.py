# -*- coding: utf-8 -*-
"""A written hour followed by "and" keeps what follows, it.

A fraction after the hour is its half or its quarter: "alle 10h e mezza" reads as "alle 10 e mezza".
A count of something else after "and" is not minutes, so the clock stays.
Anchor 2017-06-27 13:04: 10:00 has gone, so 10:xx is tomorrow; 20:xx is
still ahead today.
"""
import pytest

from ._corpus import span


@pytest.mark.parametrize("text,day,hour,minute", [
    ("alle 10h e mezza", 28, 10, 30),
    ("alle 10:00 e mezza", 28, 10, 30),
])
def test_a_fraction_after_a_written_hour(text, day, hour, minute):
    s = span(text)
    assert (s.start.month, s.start.day) == (6, day)
    assert (s.start.hour, s.start.minute) == (hour, minute)
