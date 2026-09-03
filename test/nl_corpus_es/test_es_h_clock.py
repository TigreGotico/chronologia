# -*- coding: utf-8 -*-
"""The hour-letter clock: "21h30" and "20h".

Iberian Romance writes the clock two ways.  The colon form dominates, and
beside it runs the hour-letter form shared with Portuguese and French.  It
is attested in running prose on this language's Wikipedia -- Spanish TV
schedules and an Ecuadorian decree, the 1949 Turia flood in Catalan, RTP
Acores listings in Galician -- so the parser reads it.

The controls matter as much as the readings.  An hour above 23 and a
minute above 59 are not clock times, and the "h" of a speed must never
open one.
"""
import pytest

from ._corpus import nomatch, parse


@pytest.mark.parametrize("text,h,m", [
    ("21h30", 21, 30),
    ("20h", 20, 0),
    ("0h15", 0, 15),
    ("9h05", 9, 5),
    ("23h59", 23, 59),
])
def test_hour_letter_clock(text, h, m):
    r = parse(text)
    assert r is not None, text
    assert (r[0].start.hour, r[0].start.minute) == (h, m)
    assert r[1] == ""


@pytest.mark.parametrize("text", ["25h", "24h30", "20h70", "20h60"])
def test_an_impossible_clock_is_not_one(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["100 km/h", "a 100 km/h"])
def test_a_speed_is_not_a_clock(text):
    nomatch(text)
