# -*- coding: utf-8 -*-
"""The "week of <date>" construction for hu: widen a date to its week."""
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
    ('a hét 2026. július 20.', (2026, 7, 20)),
    ('a hét 2026. január 15.', (2026, 1, 15)),
    ('a hét 2026. december 10.', (2026, 12, 10)),
    ('a hét 2026. március 5.', (2026, 3, 5)),
    ('a hét 2026. július 4.', (2026, 7, 4)),
    ('a hét 2026. március 11.', (2026, 3, 11)),
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
    MN = {7: 'július', 1: 'január', 12: 'december', 3: 'március', 6: 'június', 8: 'augusztus'}
    text = '{y}. {M} {d}.'.format(d=ymd[2], M=MN[ymd[1]], y=ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'a hét',
    'hét',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
