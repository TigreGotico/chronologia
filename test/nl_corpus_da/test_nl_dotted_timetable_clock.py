# -*- coding: utf-8 -*-
"""(da): the dotted timetable clock, and the date it must not swallow.

Danish writes a timetable time with a full stop rather than a colon, so
``14.30`` is half past two in the afternoon.  The same punctuation writes a
date, which is why the refusals below matter more than the reading: a dotted
pair is a clock only when both halves are in range, and a dated form with its
year stays a date.
"""
import pytest

from ._corpus import ANCHOR, clk, nomatch, start


@pytest.mark.parametrize("text,h,mi", [
    ('14.30', 14, 30),
    ('14.03', 14, 3),
    ('0.30', 0, 30),
    ('mødet er 14.30', 14, 30),
])
def test_dotted_clock_reads(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text", [
    '24.30',   # no twenty-fourth hour
    '12.60',   # no sixtieth minute
    '1.5',     # a bare pair that is neither a clock nor a date
])
def test_out_of_range_dotted_pair_refuses(text):
    nomatch(text)


def test_dated_form_is_still_a_date():
    """The disambiguator the whole construction rests on.

    ``14.3.2018`` carries its year, so it is the fourteenth of March and not
    fourteen minutes past three.  A dotted-clock reading that captured this
    would turn every written Danish date into a time.
    """
    span = start('14.3.2018')
    assert span.year == 2018
    assert span.month == 3
    assert span.day == 14
