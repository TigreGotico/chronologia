"""fy: day-part qualifiers on a named day.

moarns (morning), middeis (afternoon), jûns (evening), nachts (night) name the
Netherlands-convention time-of-day bands (CLDR nl boundaries; West Frisian
shares them) with Frisian surfaces.  A day-part NARROWS its span to that band:
"moarn moarns" is tomorrow's morning [06:00, 12:00), not the whole day; a bare
day-part resolves to today's band.  (The bare noun 'moarn' stays "tomorrow" and
'middei' stays midday -- only the adverbial forms name the bands.)
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span

_DAY = {'hjoed': 0, 'juster': -1, 'moarn': 1}
#: Frisian day-part -> (band start hour, band end hour), nl boundaries
_BAND = {'moarns': (6, 12), 'middeis': (12, 18), 'jûns': (18, 24),
         'nachts': (0, 6)}


@pytest.mark.parametrize("day", ['hjoed', 'juster', 'moarn'])
@pytest.mark.parametrize("part", ['moarns', 'middeis', 'jûns', 'nachts'])
def test_daypart_narrows_the_named_day_to_its_band(day, part):
    off = _DAY[day]
    sh, eh = _BAND[part]
    midnight = (ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0, second=0, microsecond=0)
    text = f"{day} {part}"
    assert start(text) == ad(midnight + timedelta(hours=sh))
    assert span(text).width == timedelta(hours=eh - sh)


@pytest.mark.parametrize("part", ['moarns', 'middeis', 'jûns', 'nachts'])
def test_bare_daypart_resolves_to_todays_band(part):
    sh, eh = _BAND[part]
    midnight = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    assert start(part) == ad(midnight + timedelta(hours=sh))
    assert span(part).width == timedelta(hours=eh - sh)
