# -*- coding: utf-8 -*-
"""The Nth week of a month for Bulgarian: "третата седмица на април" (the 3rd
week of April).  The week noun седмица is FEMININE and is selected with the
definite feminine ordinal (първата/втората/третата/четвъртата...).  #264 folded
only 1st/2nd; 3rd and up stranded and the whole month was returned -- a silent
wrong answer this guards against.  scoped_ordinal binds "ORD UNIT of MONTH" (the
Bulgarian connector is "на"); the definite feminine ordinal must fold to its
digit.  Weeks Monday-started; edges by independent arithmetic (anchor
2017-06-27)."""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, parse, span, start_end


def _nth_week(y, m, n):
    first = date(y, m, 1)
    first_monday = first + timedelta(days=(0 - first.weekday()) % 7)
    ws = first_monday + timedelta(days=7 * (n - 1))
    end = datetime(ws.year, ws.month, ws.day) + timedelta(days=7)
    return AstroDate(ws.year, ws.month, ws.day), AstroDate(end.year, end.month, end.day)


@pytest.mark.parametrize("text,y,m,n", [
    ('първата седмица на април', 2017, 4, 1),
    ('втората седмица на април', 2017, 4, 2),
    ('третата седмица на април', 2017, 4, 3),
    ('четвъртата седмица на април', 2017, 4, 4),
    ('трета седмица на април', 2017, 4, 3),
    ('третата седмица на май', 2017, 5, 3),
    ('четвъртата седмица на май', 2017, 5, 4),
])
def test_nth_week_of_month(text, y, m, n):
    assert start_end(text) == _nth_week(y, m, n)
    assert span(text).width.days == 7
    assert parse(text)[1] == ""
