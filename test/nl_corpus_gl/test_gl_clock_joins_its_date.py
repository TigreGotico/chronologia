# -*- coding: utf-8 -*-
"""A clock beside the date it names reads as one moment, gl.

The quarter or half after the hour stays in the clock when "no día" or "do día"
follows, so the clock and the date compose into one moment.  Anchor
2017-06-27 13:04: the next 14 March is in 2018 and 14 June has passed, so
"dia 14" is 14 July.
"""
import pytest

from ._corpus import span


def _fields(s):
    return (s.start.year, s.start.month, s.start.day, s.start.hour, s.start.minute)


@pytest.mark.parametrize("text,gold", [
    ("ás dez e cuarto no día 14 de marzo", (2018,3,14,10,15)),
    ("ás dez e cuarto do día 14 de marzo", (2018,3,14,10,15)),
    ("ás dez no día 14 de marzo", (2018,3,14,10,0)),
    ("ás dez e media no día 14 de marzo", (2018,3,14,10,30)),
])
def test_clock_joins_the_date(text, gold):
    s = span(text)
    assert _fields(s) == gold


@pytest.mark.parametrize("text,gold", [
    ("ás dez e cuarto", (2017,6,27,22,15)),
    ("o día 14 de marzo", (2018,3,14,0,0)),
])
def test_alone_keeps_its_reading(text, gold):
    assert _fields(span(text)) == gold
