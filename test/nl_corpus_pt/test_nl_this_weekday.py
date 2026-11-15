# -*- coding: utf-8 -*-
"""\"esta <weekday>\" is the first such weekday on or after the anchor, pt.

A named occurrence is the next one after the anchor, and the anchor day
itself when it is that day.  Said on Saturday 2017-07-01, "esta segunda" is
Monday 2017-07-03, not the Monday already past; "esta sexta" is Friday
2017-07-07; "este sábado" is the anchor day.  Said on Tuesday 2017-06-27,
"esta segunda" is Monday 2017-07-03 and "esta terça" is the anchor day.
Counted on the calendar by hand.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

SATURDAY = datetime(2017, 7, 1, 13, 4)
TUESDAY = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("text,anchor,ymd", [
    ("esta segunda", SATURDAY, (2017, 7, 3)),
    ("esta segunda-feira", SATURDAY, (2017, 7, 3)),
    ("esta sexta", SATURDAY, (2017, 7, 7)),
    ("este sábado", SATURDAY, (2017, 7, 1)),
    ("este domingo", SATURDAY, (2017, 7, 2)),
    ("esta segunda-feira", TUESDAY, (2017, 7, 3)),
    ("esta terça-feira", TUESDAY, (2017, 6, 27)),
    ("esta quarta", TUESDAY, (2017, 6, 28)),
])
def test_this_weekday(text, anchor, ymd):
    span, rest = extract_timespan(text, "pt", anchor)
    assert span.start == AstroDate(*ymd)
    assert rest == ""
