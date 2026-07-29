# -*- coding: utf-8 -*-
"""nl: a postposed genitive daypart shifts a 12-hour clock into 24-hour form.

Idiomatic Dutch disambiguates a bare 12-hour reading with a trailing
"'s <daypart>s" phrase.  The afternoon/evening half (middag [12:00, 18:00),
avond [18:00, 24:00)) is pm and adds twelve; the morning/night half
(ochtend [06:00, 12:00), nacht [00:00, 06:00)) is am and leaves the hour,
rewriting only the noon/midnight edge.  Bands: Unicode CLDR 47 Day Period
Rules, locale nl (transcribed in chronologia.dayparts).

Gold is hand-derived from the sentence, never pinned from the engine.
Anchor: Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import clk, span

_HOURS = {
    1: "een", 2: "twee", 3: "drie", 4: "vier", 5: "vijf", 6: "zes",
    7: "zeven", 8: "acht", 9: "negen", 10: "tien", 11: "elf", 12: "twaalf",
}


def _pm(h):
    return h + 12 if h < 12 else 12


def _am(h):
    return 0 if h == 12 else h


@pytest.mark.parametrize("h", sorted(_HOURS))
@pytest.mark.parametrize("part,shift", [("avonds", _pm), ("middags", _pm),
                                        ("ochtends", _am), ("nachts", _am)])
def test_hour_times_daypart(h, part, shift):
    text = f"{_HOURS[h]} uur 's {part}"
    assert span(text).start == clk(shift(h), 0)


def test_evening_noon_edge_stays_twelve():
    assert span("twaalf uur 's avonds").start == clk(12, 0)


def test_night_midnight_edge_wraps_to_zero():
    assert span("twaalf uur 's nachts").start == clk(0, 0)


@pytest.mark.parametrize("text,h,mi", [
    ("kwart over drie 's middags", 15, 15),
    ("kwart voor negen 's avonds", 20, 45),
    ("half twee 's middags", 13, 30),
])
def test_fractional_readings_shift(text, h, mi):
    assert span(text).start == clk(h, mi)
