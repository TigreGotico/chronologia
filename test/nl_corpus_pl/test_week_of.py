# -*- coding: utf-8 -*-
"""The "week of <date>" construction for pl: widen a date to its week."""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, nomatch, parse, span, start_end


def _week(y, m, d):
    day = date(y, m, d)
    ws = day - timedelta(days=day.weekday())
    start = AstroDate(ws.year, ws.month, ws.day)
    end_dt = datetime(ws.year, ws.month, ws.day) + timedelta(days=7)
    return start, AstroDate(end_dt.year, end_dt.month, end_dt.day)


@pytest.mark.parametrize("text,ymd", [
    ('tydzień od 20 lipca 2026', (2026, 7, 20)),
    ('tydzień od 15 stycznia 2026', (2026, 1, 15)),
    ('tydzień od 10 grudnia 2026', (2026, 12, 10)),
    ('tydzień od 5 marca 2026', (2026, 3, 5)),
    ('tydzień od 4 lipca 2026', (2026, 7, 4)),
    ('tydzień od 11 marca 2026', (2026, 3, 11)),
])
def test_week_of(text, ymd):
    s, e = start_end(text)
    assert (s, e) == _week(*ymd)
    assert span(text).width.days == 7
    assert parse(text)[1] == ""


@pytest.mark.parametrize("ymd", [
    (2026, 7, 20),
    (2026, 1, 15),
    (2026, 12, 10),
    (2026, 3, 5),
])
def test_bare_date_is_a_single_day(ymd):
    MN = {7: 'lipca', 1: 'stycznia', 12: 'grudnia', 3: 'marca', 6: 'czerwca', 8: 'sierpnia'}
    text = "%d %s %d" % (ymd[2], MN[ymd[1]], ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'tydzień od',
    'tydzień z',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
