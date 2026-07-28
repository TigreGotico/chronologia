# -*- coding: utf-8 -*-
"""Slovak dayparts on a named relative day: "zajtra ráno", "včera večer".

A daypart word (ráno / popoludní / večer, CLDR sk bands) narrows a named
relative day to its band.  The day is the deictic offset from the anchor
(dnes 0, zajtra +1, včera -1, pozajtra +2, predvčerom -2); the band supplies
the hours.  Bounds are the offset day at the band edges, computed directly.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import span, ANCHOR

# band -> (start_hour, end_hour)
_BAND = {"ráno": (4, 12), "popoludní": (12, 18), "večer": (18, 22)}
_DAY = {"dnes": 0, "zajtra": 1, "včera": -1, "pozajtra": 2, "predvčerom": -2}


def _expected(day, band):
    d = (ANCHOR + timedelta(days=_DAY[day])).date()
    sh, eh = _BAND[band]
    return (AstroDate(d.year, d.month, d.day, sh, 0),
            AstroDate(d.year, d.month, d.day, eh, 0))


@pytest.mark.parametrize("band", list(_BAND))
@pytest.mark.parametrize("day", list(_DAY))
def test_relative_day_band(day, band):
    text = f"{day} {band}"
    s = span(text)
    assert (s.start, s.end) == _expected(day, band), text


@pytest.mark.parametrize("band", list(_BAND))
def test_bare_band_today(band):
    """A bare daypart lands on the anchor day at its band edges."""
    s = span(band)
    assert (s.start, s.end) == _expected("dnes", band), band
