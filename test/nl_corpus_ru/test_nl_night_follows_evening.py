"""Russian "ночью" names the night after the named day's evening.

"ночь" is "Часть суток от захода до восхода солнца, от вечера до утра"
(gramota.ru, s.v. ночь, sense 1).  The ru night band is the small hours, 00:00
to 04:00 (CLDR 47, ru), so the night of a day is that band on the NEXT civil
date.  At the Tuesday 27 June 2017 13:04 anchor, "сегодня ночью" and bare
"ночью" are the coming night, 28 June 00:00-04:00, not this morning's night,
which has passed.  "завтра ночью" is the night after Wednesday evening, and
"вчера ночью" is the night after Monday evening, this morning.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse


@pytest.mark.parametrize("text,day", [
    ("сегодня ночью", 28),
    ("ночью", 28),
    ("какая погода будет сегодня ночью", 28),
    ("завтра ночью", 29),
    ("вчера ночью", 27),
])
def test_night_band(text, day):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(datetime(2017, 6, day, 0, 0))
    assert r.span.end == ad(datetime(2017, 6, day, 4, 0))


@pytest.mark.parametrize("text,day,hour", [
    ("сегодня ночью в 3", 28, 3),
    ("завтра ночью в 3 часа", 29, 3),
])
def test_clock_in_the_night(text, day, hour):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(datetime(2017, 6, day, hour, 0))
    assert r.remainder == ""
