"""fy: day-part qualifiers on a named day.

moarns (morning), middeis (afternoon/midday), jûns (evening), nachts (night)
attach to hjoed/juster/moarn.  The current engine resolves these to the whole
target DAY (the day-part does not narrow the span); we assert the day, which is
the certain, well-defined part of the result.  The bare day-part alone does not
resolve -- see the module-level note.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span, nomatch

_DAY = {'hjoed': 0, 'juster': -1, 'moarn': 1}


@pytest.mark.parametrize("day", ['hjoed', 'juster', 'moarn'])
@pytest.mark.parametrize("part", ['moarns', 'middeis', 'jûns', 'nachts'])
def test_daypart_resolves_to_day(day, part):
    off = _DAY[day]
    base = (ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0, second=0, microsecond=0)
    text = f"{day} {part}"
    assert start(text) == ad(base)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("part", ['moarns', 'middeis', 'jûns', 'nachts'])
def test_bare_daypart_does_not_resolve(part):
    # a day-part with no anchoring day is not a datable span
    nomatch(part)
