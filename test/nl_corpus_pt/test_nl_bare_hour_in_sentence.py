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


@pytest.mark.parametrize("text,day,hour", [
    ("15h", 27, 15),
    ("às 15h", 27, 15),
    ("amanhã 15h", 28, 15),
])
def test_a_clock_alone_or_after_a_marker_still_reads(text, day, hour):
    s = span(text)
    assert (s.start.month, s.start.day, s.start.hour) == (6, day, hour)
