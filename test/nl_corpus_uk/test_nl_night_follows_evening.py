"""Ukrainian "вночі" names the night after the named day's evening.

"ніч" is "Частина доби від заходу до сходу сонця, з вечора до ранку" (СУМ-11,
s.v. ніч).  The uk night band is the small hours, 00:00 to 04:00 (CLDR 47, uk),
so the night of a day is that band on the NEXT civil date.  At the Tuesday 27
June 2017 13:04 anchor, "сьогодні вночі" and bare "вночі" are 28 June
00:00-04:00, and "завтра вночі" is 29 June 00:00-04:00.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse


@pytest.mark.parametrize("text,day", [
    ("сьогодні вночі", 28),
    ("вночі", 28),
    ("завтра вночі", 29),
])
def test_night_band(text, day):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(datetime(2017, 6, day, 0, 0))
    assert r.span.end == ad(datetime(2017, 6, day, 4, 0))


def test_clock_in_the_night():
    r = parse("сьогодні вночі о 3")
    assert r is not None
    assert r.span.start == ad(datetime(2017, 6, 28, 3, 0))
    assert r.remainder == ""
