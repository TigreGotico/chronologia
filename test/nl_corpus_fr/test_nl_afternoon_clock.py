# -*- coding: utf-8 -*-
"""The "de l'après-midi" meridiem (fr): "trois heures de l'après-midi" = 15:00.

This is distinct from the bare "après-midi" day-part band (R165, see
test_nl_r165_apres_midi): the post-posed meridiem phrase "... de l'après-midi"
composes with a spelled hour to add twelve hours, the afternoon counterpart
of "du matin" / "du soir" already covered in test_nl_clock.

Anchor Tuesday 2017-06-27 13:04.  15:00-17:00 are all still ahead of 13:04, so
they stay on the anchor day; a clock reference is one minute wide.
"""
import pytest

from ._corpus import span, start, nomatch, AstroDate


@pytest.mark.parametrize("text,h", [
    ("deux heures de l'après-midi", 14),
    ("trois heures de l'après-midi", 15),
    ("quatre heures de l'après-midi", 16),
    ("cinq heures de l'après-midi", 17),
])
def test_afternoon_meridiem(text, h):
    assert start(text) == AstroDate(2017, 6, 27, h, 0)
    # the leading "à" is optional and must not change the reading
    assert start("à " + text) == AstroDate(2017, 6, 27, h, 0)


def test_afternoon_clock_is_minute_wide():
    from datetime import timedelta
    assert span("trois heures de l'après-midi").width == timedelta(minutes=1)


def test_afternoon_adds_twelve_hours_over_bare_hour():
    # the meridiem is what turns 3 into 15; the bare hour rolls to next day 03h
    assert start("trois heures de l'après-midi") == AstroDate(2017, 6, 27, 15, 0)
    assert start("à trois heures") == AstroDate(2017, 6, 28, 3, 0)
