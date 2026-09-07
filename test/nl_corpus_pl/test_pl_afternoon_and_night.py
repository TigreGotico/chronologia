# -*- coding: utf-8 -*-
"""The Polish afternoon and night.

Polish declares four parts of the day and named only two of them, so
"rano" and "wieczorem" read while "po południu" and "w nocy" fell out and
left the phrase answering midnight.

Surfaces come from CLDR 47: the format chart gives the phrase a speaker
places an event with, the stand-alone chart the bare noun.
"""
import pytest

from ._corpus import parse


@pytest.mark.parametrize("text,hour", [
    ("po południu", 12),
    ("dzisiaj po południu", 12),
    ("jutro po południu", 12),
    ("popołudnie", 12),
])
def test_the_afternoon_is_read(text, hour):
    got = parse(text)
    assert got is not None, text
    assert got[0].start.hour == hour
    assert got[1] == ""


@pytest.mark.parametrize("text,hour", [
    ("w nocy", 21),
    ("dzisiaj w nocy", 21),
    ("noc", 21),
])
def test_the_night_is_read(text, hour):
    got = parse(text)
    assert got is not None, text
    assert got[0].start.hour == hour
    assert got[1] == ""


@pytest.mark.parametrize("text,hour", [("dzisiaj rano", 6), ("dzisiaj wieczorem", 18)])
def test_the_two_that_already_read_are_unchanged(text, hour):
    got = parse(text)
    assert got[0].start.hour == hour
    assert got[1] == ""
