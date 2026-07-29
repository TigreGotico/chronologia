# -*- coding: utf-8 -*-
"""da: a postposed "om <daypart>" phrase shifts a 12-hour clock into 24h form.

Danish disambiguates a bare 12-hour reading with a trailing "om
<daypart>en".  The afternoon/evening half (eftermiddag [12:00, 18:00),
aften [18:00, 24:00)) is pm and adds twelve; the morning/night half
(nat [00:00, 05:00), formiddag [10:00, 12:00)) is am and leaves the hour,
rewriting only the noon/midnight edge.  Bands: Unicode CLDR 47 Day Period
Rules, locale da (transcribed in chronologia.dayparts).

Gold is hand-derived from the sentence, never pinned from the engine.
Anchor: Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import clk, span

# Hour 2 ("to") is deliberately omitted from the bare-hour sweep: the Danish
# number word "to" is a homograph of the range connector "to", which the
# pre-fold range splitter treats as a "A to B" boundary before the clock is
# read.  That collision is a pre-existing locale defect independent of the
# daypart shift under test here (it already mis-parses "klokken to over tre"
# on the unmodified locale), so hour 2 is covered only via forms that never
# expose a bare "to" token (the fractional "halv to ..." case below).
_HOURS = {
    1: "et", 3: "tre", 4: "fire", 5: "fem", 6: "seks",
    7: "syv", 8: "otte", 9: "ni", 10: "ti", 11: "elleve", 12: "tolv",
}


def _pm(h):
    return h + 12 if h < 12 else 12


def _am(h):
    return 0 if h == 12 else h


@pytest.mark.parametrize("h", sorted(_HOURS))
@pytest.mark.parametrize("part,shift", [("eftermiddagen", _pm), ("aftenen", _pm),
                                        ("formiddagen", _am), ("natten", _am)])
def test_hour_times_daypart(h, part, shift):
    text = f"klokken {_HOURS[h]} om {part}"
    assert span(text).start == clk(shift(h), 0)


def test_evening_noon_edge_stays_twelve():
    assert span("klokken tolv om aftenen").start == clk(12, 0)


def test_night_midnight_edge_wraps_to_zero():
    assert span("klokken tolv om natten").start == clk(0, 0)


@pytest.mark.parametrize("text,h,mi", [
    ("kvart over tre om eftermiddagen", 15, 15),
    ("kvart i ni om aftenen", 20, 45),
    ("halv to om eftermiddagen", 13, 30),
])
def test_fractional_readings_shift(text, h, mi):
    assert span(text).start == clk(h, mi)
