# -*- coding: utf-8 -*-
"""A day of the relative month ("o dia 5 do mês que vem") and a quarter-hour offset.

Expected values are hand arithmetic from the anchor 2017-06-27 13:04."""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start, start_end, nomatch

DAY = timedelta(days=1)


def _day(y, m, d):
    return datetime(y, m, d), datetime(y, m, d) + DAY


@pytest.mark.parametrize("text,expected", [
    ("o dia 5 do mês que vem", _day(2017, 7, 5)),
    ("dia 5 do próximo mês", _day(2017, 7, 5)),
    ("no dia 15 do mês que vem", _day(2017, 7, 15)),
    ("o dia 5 do mês passado", _day(2017, 5, 5)),
    ("dia 31 do mês que vem", _day(2017, 7, 31)),
])
def test_day_of_relative_month(text, expected):
    """The anchor is Tuesday 2017-06-27, so the next month is July 2017."""
    s, e = start_end(text)
    assert (s, e) == (ad(expected[0]), ad(expected[1]))


@pytest.mark.parametrize("text", [
    "o dia 30 do mês que vem",
])
def test_day_of_relative_month_refused_when_absent(text):
    """February has no 30th: the reading is refused, never clamped."""
    nomatch(text, anchor=datetime(2017, 1, 31, 9, 0))


@pytest.mark.parametrize("text", [
    "o dia 5 do mês anterior",
    "dia 5 do mês anterior",
])
def test_previous_month_is_never_read_as_next(text):
    """The previous month is May 2017: the phrase reads as 2017-05-05 or is
    refused, and never answers July with the marker left over."""
    r = parse(text)
    if r is not None:
        assert r.span.start == ad(datetime(2017, 5, 5))
        assert r.remainder == ""


@pytest.mark.parametrize("text,minutes", [
    ("daqui a um quarto de hora", 15),
    ("dentro de um quarto de hora", 15),
    ("daqui a três quartos de hora", 45),
    ("daqui a meia hora", 30),
])
def test_quarter_hour_offset(text, minutes):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(ANCHOR + timedelta(minutes=minutes))
    assert r.remainder == ""


def test_calendar_date_with_day_label_unchanged():
    s, _ = start_end("dia 5 de março")
    assert s == ad(datetime(2018, 3, 5))
