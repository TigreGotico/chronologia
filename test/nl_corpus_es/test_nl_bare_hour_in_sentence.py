# -*- coding: utf-8 -*-
"""A bare hour inside a sentence with no clock marker is not a clock, es.

The verb that states the hour is such a marker:
"Se usa para decir la hora o fecha." (Wikcionario, s.v. "ser", 10).
Anchor 2017-06-27 13:04: 15:00 and 20:00 are still ahead today.
"""
import pytest

from ._corpus import nomatch, span


def test_the_verb_that_states_the_hour_marks_a_clock():
    s = span("son las 15h")
    assert (s.start.month, s.start.day, s.start.hour, s.start.minute) == (
        6, 27, 15, 0)


@pytest.mark.parametrize("text", ["sobre las 20h", "hacia las 20h"])
def test_a_word_of_approximation_marks_a_clock(text):
    """"sobre [...] 7. Referido al tiempo, indica que se está cerca de un
    momento determinado. Sinónimos: hacia, cerca de." (Wikcionario)."""
    s = span(text)
    assert (s.start.month, s.start.day, s.start.hour, s.start.minute) == (
        6, 27, 20, 0)


def test_a_length_with_a_fraction_is_not_a_clock():
    """A bare hour with no marker is not a clock, and a half after it does
    not make it one."""
    nomatch("una película de 2h y media")
