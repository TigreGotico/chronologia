# -*- coding: utf-8 -*-
"""A bare hour inside a sentence with no clock marker is not a clock, pt.

"15h" is a clock when it is the whole utterance or follows a clock marker
("às").  Inside a sentence with no marker it is as often a length ("um filme
de 2h") and is not read.  Anchor 2017-06-27 13:04: 15:00 is still ahead
today.
"""
import pytest

from ._corpus import nomatch, span


@pytest.mark.parametrize("text", ["um filme de 2h", "uma viagem de 3h"])
def test_a_length_in_a_sentence_is_not_a_clock(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "um filme de 2h e meia",
    "um filme de 2h e um quarto",
])
def test_a_length_with_a_fraction_is_not_a_clock(text):
    """A half or a quarter after the hour does not make it a clock: the
    length is still a bare hour with no marker."""
    nomatch(text)


@pytest.mark.parametrize("text,day,hour", [
    ("15h", 27, 15),
    ("às 15h", 27, 15),
    ("amanhã 15h", 28, 15),
])
def test_a_clock_alone_or_after_a_marker_still_reads(text, day, hour):
    s = span(text)
    assert (s.start.month, s.start.day, s.start.hour) == (6, day, hour)


@pytest.mark.parametrize("text,day,hour", [
    ("são 15h", 27, 15),
    ("já são 15h", 27, 15),
])
def test_the_verb_that_states_the_hour_marks_a_clock(text, day, hour):
    """"ser [...] 14. Indica o momento [...] (ex.: já é noite; são 18h00)."
    (Priberam, s.v. "ser")."""
    s = span(text)
    assert (s.start.month, s.start.day, s.start.hour) == (6, day, hour)


@pytest.mark.parametrize("text,day,hour", [
    ("por volta das 20h", 27, 20),
    ("a partir das 20h", 27, 20),
])
def test_a_word_of_approximation_or_start_marks_a_clock(text, day, hour):
    """"Cerca de, por volta de, próximo de" (Priberam, s.v. "volta"); "a
    partir de: Com início em determinada data" (Priberam, s.v. "partir")."""
    s = span(text)
    assert (s.start.month, s.start.day, s.start.hour) == (6, day, hour)
