# -*- coding: utf-8 -*-
"""The "week of <date>" construction for gl: widen a date to its week."""
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
    ('a semana do 20 de xullo de 2026', (2026, 7, 20)),
    ('a semana do 15 de xaneiro de 2026', (2026, 1, 15)),
    ('a semana do 10 de decembro de 2026', (2026, 12, 10)),
    ('a semana do 5 de marzo de 2026', (2026, 3, 5)),
    ('a semana do 4 de xullo de 2026', (2026, 7, 4)),
    ('a semana do 11 de marzo de 2026', (2026, 3, 11)),
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
    MN = {7: 'xullo', 1: 'xaneiro', 12: 'decembro', 3: 'marzo', 6: 'xuño'}
    text = "{d} de {M} de {y}".format(d=ymd[2], M=MN[ymd[1]], y=ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'a semana do',
    'semana do',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
