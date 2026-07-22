# -*- coding: utf-8 -*-
"""The "week of <date>" construction for ast: widen a date to its week."""
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
    ('la selmana del 20 de xunetu 2026', (2026, 7, 20)),
    ('la selmana del 15 de xineru 2026', (2026, 1, 15)),
    ('la selmana del 10 de avientu 2026', (2026, 12, 10)),
    ('la selmana del 5 de marzu 2026', (2026, 3, 5)),
    ('la selmana del 4 de xunetu 2026', (2026, 7, 4)),
    ('la selmana del 11 de marzu 2026', (2026, 3, 11)),
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
    MN = {7: 'xunetu', 1: 'xineru', 12: 'avientu', 3: 'marzu', 6: 'xunu'}
    text = "{d} de {M} {y}".format(d=ymd[2], M=MN[ymd[1]], y=ymd[0])
    assert span(text).width.days == 1


@pytest.mark.parametrize("text", [
    'la selmana del',
    'selmana del',
])
def test_marker_without_a_date_does_not_parse(text):
    nomatch(text)
