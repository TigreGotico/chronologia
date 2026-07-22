# -*- coding: utf-8 -*-
"""The "week of <date>" construction for an: widen a date to its week."""
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
    ('a semana de 20 de chuliol de 2026', (2026, 7, 20)),
    ('a semana de 15 de chinero de 2026', (2026, 1, 15)),
    ('a semana de 10 de deciembre de 2026', (2026, 12, 10)),
    ('a semana de 5 de marzo de 2026', (2026, 3, 5)),
    ('a semana de 4 de chuliol de 2026', (2026, 7, 4)),
    ('a semana de 11 de marzo de 2026', (2026, 3, 11)),
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
    MN = {7: 'chuliol', 1: 'chinero', 12: 'deciembre', 3: 'marzo', 6: 'chunyo'}
    text = "{d} de {M} de {y}".format(d=ymd[2], M=MN[ymd[1]], y=ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'a semana de',
    'semana de',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
