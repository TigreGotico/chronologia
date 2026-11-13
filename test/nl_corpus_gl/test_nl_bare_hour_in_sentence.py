# -*- coding: utf-8 -*-
"""A bare hour inside a sentence with no clock marker is not a clock, gl.

The verb that states the hour is such a marker:
"-Que hora é? -Son as catro." (RAG, s.v. "hora", 2).
Anchor 2017-06-27 13:04: 15:00 is still ahead today.
"""
from ._corpus import span


def test_the_verb_that_states_the_hour_marks_a_clock():
    s = span("son as 15h")
    assert (s.start.month, s.start.day, s.start.hour, s.start.minute) == (
        6, 27, 15, 0)
