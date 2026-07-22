# -*- coding: utf-8 -*-
"""The "week of <date>" construction for ro: widen a date to its week."""
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
    ('săptămâna din 20 iulie 2026', (2026, 7, 20)),
    ('săptămâna din 15 ianuarie 2026', (2026, 1, 15)),
    ('săptămâna din 10 decembrie 2026', (2026, 12, 10)),
    ('săptămâna din 5 martie 2026', (2026, 3, 5)),
    ('săptămâna din 4 iulie 2026', (2026, 7, 4)),
    ('săptămâna din 11 martie 2026', (2026, 3, 11)),
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
    MN = {7: 'iulie', 1: 'ianuarie', 12: 'decembrie', 3: 'martie', 6: 'iunie'}
    text = "{d} {M} {y}".format(d=ymd[2], M=MN[ymd[1]], y=ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'săptămâna din',
    'saptamana din',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
