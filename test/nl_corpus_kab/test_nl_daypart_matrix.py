# -*- coding: utf-8 -*-
"""Kabyle daypart bands, full surface sweep (morning/evening/night).

Surfaces attested by native speaker athmanemokraoui
(TigreGotico/chronologia#265): ṣṣbeḥ / taṣebḥit = morning, tameddit =
(late) afternoon / evening, iḍ = night; the ``-a`` proximal-deictic suffix
and the ``ass-a`` ("today") prefix both mean "this <part> of today".

Band boundaries fall back to chronologia's default day-period convention
(morning 06-12, evening 18-21, night 21-06 crossing midnight); the native
speaker did not supply Kabyle-specific clock boundaries. Gold is the anchor
day (2017-06-27) since a bare daypart is not future-shifted within the day.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, span

# daypart surface -> (start_hour, end_hour, end_day_offset)
BANDS = {
    "ṣṣbeḥ": (6, 12, 0),
    "taṣebḥit": (6, 12, 0),
    "tameddit": (18, 21, 0),
    "iḍ": (21, 6, 1),
}

_TODAY = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)


def _band(day, part):
    h0, h1, off = BANDS[part]
    s = day.replace(hour=h0)
    e = (day + timedelta(days=off)).replace(hour=h1)
    return s, e


# every daypart, plain + '-a' proximal suffix + 'ass-a ' ("today") prefix
_SURFACES = []
for _p in BANDS:
    _SURFACES.append((_p, _p))
    _SURFACES.append(("%s-a" % _p, _p))
    _SURFACES.append(("ass-a %s" % _p, _p))


@pytest.mark.parametrize("text,part", _SURFACES)
def test_daypart_band(text, part):
    sp = span(text)
    s, e = _band(_TODAY, part)
    assert sp.start_datetime == s
    assert sp.end_datetime == e
