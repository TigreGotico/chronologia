# -*- coding: utf-8 -*-
"""A written hour followed by "and" keeps what follows, es.

A fraction after the hour is its half or its quarter: "a las 10h y media" reads as "a las 10 y media".
A count of something else after "and" is not minutes, so the clock stays.
Anchor 2017-06-27 13:04: 10:00 has gone, so 10:xx is tomorrow; 20:xx is
still ahead today.
"""
import pytest

from ._corpus import span


@pytest.mark.parametrize("text,day,hour,minute", [
    ("a las 10h y media", 28, 10, 30),
    ("a las 10:00 y cuarto", 28, 10, 15),
])
def test_a_fraction_after_a_written_hour(text, day, hour, minute):
    s = span(text)
    assert (s.start.month, s.start.day) == (6, day)
    assert (s.start.hour, s.start.minute) == (hour, minute)


def test_a_count_of_something_else_keeps_the_clock():
    s = span("a las 10:00 y 3 personas")
    assert (s.start.month, s.start.day) == (6, 28)
    assert (s.start.hour, s.start.minute) == (10, 0)
