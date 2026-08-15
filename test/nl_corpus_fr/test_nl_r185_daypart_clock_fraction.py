# -*- coding: utf-8 -*-
"""R185: a trailing daypart qualifier ("du matin"/"du soir"/"de l'après-midi")
binds the clock's MERIDIEM slot when it follows a bare hour ("trois heures du
matin"), but stranded as remainder once a fraction sat between the hour and
the qualifier ("trois heures et demie de l'après-midi" read 03:30 instead of
15:30): the ``clock_time`` orders that route through FRACTION/MINUTE lacked
the "of?" connector ("de"/"du"/"des"/"d") that the plain-hour orders carry
before "article? MERIDIEM?", so "de l'après-midi" could not be consumed after
a fraction and the whole qualifier fell into the remainder, leaving the clock
on its bare AM reading. pt/es already carry "of? article?" after every
FRACTION/MINUTE slot in their own ``clock_time`` orders; fr's orders now
match that shape.

Anchor is the shared corpus ANCHOR, Tuesday 2017-06-27 13:04. Gold hours are
computed here by hand from the fr meridiem mapping ("matin" -> hour as
spoken, "après-midi"/"soir" -> hour + 12) and the ordinary prefer_future roll
(an hour already past today lands tomorrow).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span


def _clk(hour, minute=0):
    dt = ANCHOR.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


# -- fraction intervening between the hour and the trailing daypart --
@pytest.mark.parametrize("text,hour,minute", [
    ("à trois heures et demie de l'après-midi", 15, 30),
    ("trois heures et demie de l'après-midi", 15, 30),
    ("à 3 heures et demie de l'après-midi", 15, 30),
    ("à quatre heures et quart du matin", 4, 15),
    ("à onze heures et demie du soir", 23, 30),
    ("à 11 heures et quart du soir", 23, 15),
    ("trois heures moins le quart de l'après-midi", 14, 45),
])
def test_fraction_then_daypart_qualifier(text, hour, minute):
    assert start(text) == _clk(hour, minute)
    assert span(text).width == timedelta(minutes=1)


# -- plain hour + trailing daypart, no fraction (must not regress) --
@pytest.mark.parametrize("text,hour", [
    ("à trois heures du matin", 3),
    ("à onze heures du soir", 23),
    ("à trois heures de l'après-midi", 15),
])
def test_plain_hour_daypart_qualifier(text, hour):
    assert start(text) == _clk(hour)
    assert span(text).width == timedelta(minutes=1)
