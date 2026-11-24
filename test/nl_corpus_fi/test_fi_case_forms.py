# -*- coding: utf-8 -*-
"""Finnish case forms of a clock hour and of a weekday.

"puoli seitsemältä" is the half hour toward seven, 6:30, with the hour in the
ablative; "maanantaiksi" is the translative of "maanantai".  Anchor: Tuesday
2017-06-27 13:04.  A lone hour takes the next twelve-hour reading (ruling 17),
so 6:30 is 18:30 the same day, and the next Monday is 2017-07-03.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1019"
ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_half_hour_with_an_ablative_hour():
    found = extract_timespan("herätä minut puoli seitsemältä", "fi", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 6, 27, 18, 30)
    assert found.remainder == "herätä minut"


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_translative_weekday_with_a_clock():
    found = extract_timespan(
        "aseta uusi herätys maanantaiksi kello seitsemän", "fi", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 7, 3, 7, 0)
