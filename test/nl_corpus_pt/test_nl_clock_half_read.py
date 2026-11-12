# -*- coding: utf-8 -*-
"""A written hour followed by "and" keeps what follows, pt.

A fraction after the hour is its half or its quarter: "às 10h e meia" reads as "às 10 e meia".
A count of something else after "and" is not minutes, so the clock stays.
Anchor 2017-06-27 13:04: 10:00 has gone, so 10:xx is tomorrow; 20:xx is
still ahead today.
"""
import pytest

from ._corpus import span


@pytest.mark.parametrize("text,day,hour,minute", [
    ("às 10h e meia", 28, 10, 30),
    ("às 10:00 e meia", 28, 10, 30),
    ("às 10h e um quarto", 28, 10, 15),
    ("às 20h e meia", 27, 20, 30),
])
def test_a_fraction_after_a_written_hour(text, day, hour, minute):
    s = span(text)
    assert (s.start.month, s.start.day) == (6, day)
    assert (s.start.hour, s.start.minute) == (hour, minute)


def test_a_count_of_something_else_keeps_the_clock():
    s = span("chego às 10:00 e 2 amigos vêm comigo")
    assert (s.start.month, s.start.day) == (6, 28)
    assert (s.start.hour, s.start.minute) == (10, 0)
