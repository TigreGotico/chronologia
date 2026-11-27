# -*- coding: utf-8 -*-
"""The Nth week of a month for Russian: "третья неделя апреля" (3rd week of
April).  The week noun неделя is FEMININE, so the selecting ordinal carries the
feminine nominative ending (первая/вторая/третья/четвёртая...).  #264 folded
only 1st/2nd; 3rd and up stranded and the whole month was returned -- a silent
wrong answer this guards against.  scoped_ordinal binds "ORD UNIT MONTH"; the
feminine ordinal must fold to its digit for the ORD slot.  Weeks are Monday-
started; edges by independent arithmetic (anchor 2017-06-27).  With no year the month takes the year the month alone takes
(ruling 1, changed 26 November 2026): April and May have ended at the anchor, so 2018."""
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


# April 2018 has 5 Monday-weeks (02, 09, 16, 23, 30); May 2018 has 4 (07, 14, 21, 28).
@pytest.mark.parametrize("text,y,m,n", [
    # ruling 1 (changed 26 November 2026): April and May have ended at the anchor, so they are 2018
    ('первая неделя апреля', 2018, 4, 1),
    ('вторая неделя апреля', 2018, 4, 2),
    ('третья неделя апреля', 2018, 4, 3),
    ('четвёртая неделя апреля', 2018, 4, 4),
    ('четвертая неделя апреля', 2018, 4, 4),
    ('третья неделя мая', 2018, 5, 3),
    ('четвёртая неделя мая', 2018, 5, 4),
])
def test_nth_week_of_month(text, y, m, n):
    assert start_end(text) == _nth_week(y, m, n)
    assert span(text).width.days == 7
    assert parse(text)[1] == ""
