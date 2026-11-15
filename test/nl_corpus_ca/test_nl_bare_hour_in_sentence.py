# -*- coding: utf-8 -*-
"""A bare hour inside a sentence with no clock marker is not a clock, ca.

The verb that states the hour is such a marker:
"─Quina hora és? ─Són les tres" (DIEC2, s.v. "hora", 2 1).
Anchor 2017-06-27 13:04: 15:00 is still ahead today.
"""
from ._corpus import span


def test_the_verb_that_states_the_hour_marks_a_clock():
    s = span("són les 15h")
    assert (s.start.month, s.start.day, s.start.hour, s.start.minute) == (
        6, 27, 15, 0)
