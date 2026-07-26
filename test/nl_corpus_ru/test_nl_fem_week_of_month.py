# -*- coding: utf-8 -*-
"""The Nth week of a month for Russian: "третья неделя апреля" (3rd week of
April).  The week noun неделя is FEMININE, so the selecting ordinal carries the
feminine nominative ending (первая/вторая/третья/четвёртая...).  #264 folded
only 1st/2nd; 3rd and up stranded and the whole month was returned -- a silent
wrong answer this guards against.  scoped_ordinal binds "ORD UNIT MONTH"; the
feminine ordinal must fold to its digit for the ORD slot.  Weeks are Monday-
started; edges by independent arithmetic (anchor 2017-06-27)."""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, parse, span, start_end


def _nth_week(y, m, n):
    """Independent: nth Monday-started week of the month, width 7."""
    first = date(y, m, 1)
    first_monday = first + timedelta(days=(0 - first.weekday()) % 7)
    ws = first_monday + timedelta(days=7 * (n - 1))
    end = datetime(ws.year, ws.month, ws.day) + timedelta(days=7)
    return AstroDate(ws.year, ws.month, ws.day), AstroDate(end.year, end.month, end.day)


# April 2017 has 4 Monday-weeks (03, 10, 17, 24); May has 5 (01, 08, 15, 22, 29).
@pytest.mark.parametrize("text,y,m,n", [
    ('первая неделя апреля', 2017, 4, 1),
    ('вторая неделя апреля', 2017, 4, 2),
    ('третья неделя апреля', 2017, 4, 3),
    ('четвёртая неделя апреля', 2017, 4, 4),
    ('четвертая неделя апреля', 2017, 4, 4),
    ('третья неделя мая', 2017, 5, 3),
    ('четвёртая неделя мая', 2017, 5, 4),
])
def test_nth_week_of_month(text, y, m, n):
    assert start_end(text) == _nth_week(y, m, n)
    assert span(text).width.days == 7
    assert parse(text)[1] == ""
