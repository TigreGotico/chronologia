# -*- coding: utf-8 -*-
"""A day of the relative month ("el día 5 del mes que viene") and a quarter-hour offset.

Expected values are hand arithmetic from the anchor 2017-06-27 13:04."""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start, start_end, nomatch

DAY = timedelta(days=1)


def _day(y, m, d):
    return datetime(y, m, d), datetime(y, m, d) + DAY


@pytest.mark.parametrize("text,expected", [
    ("el día 5 del mes que viene", _day(2017, 7, 5)),
    ("el 5 del mes que viene", _day(2017, 7, 5)),
    ("el día 15 del próximo mes", _day(2017, 7, 15)),
    ("el día 5 del mes pasado", _day(2017, 5, 5)),
    ("el día 31 del mes que viene", _day(2017, 7, 31)),
])
def test_day_of_relative_month(text, expected):
    """The anchor is Tuesday 2017-06-27, so the next month is July 2017."""
    s, e = start_end(text)
    assert (s, e) == (ad(expected[0]), ad(expected[1]))


@pytest.mark.parametrize("text", [
    "el día 30 del mes que viene",
])
def test_day_of_relative_month_refused_when_absent(text):
    """February has no 30th: the reading is refused, never clamped."""
    nomatch(text, anchor=datetime(2017, 1, 31, 9, 0))


@pytest.mark.parametrize("text", [
    "el día 5 del mes anterior",
    "el 5 del mes anterior",
])
def test_previous_month_is_never_read_as_next(text):
    """The previous month is May 2017: the phrase reads as 2017-05-05 or is
    refused, and never answers July with the marker left over."""
    r = parse(text)
    if r is not None:
        assert r.span.start == ad(datetime(2017, 5, 5))
        assert r.remainder == ""


@pytest.mark.parametrize("text,minutes", [
    ("dentro de un cuarto de hora", 15),
    ("dentro de tres cuartos de hora", 45),
    ("en tres cuartos de hora", 45),
    ("dentro de media hora", 30),
    ("hace un cuarto de hora", -15),
    ("hace media hora", -30),
])
def test_quarter_hour_offset(text, minutes):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(ANCHOR + timedelta(minutes=minutes))
    assert r.remainder == ""


def test_calendar_date_with_day_label_unchanged():
    s, _ = start_end("el día 5 de marzo")
    assert s == ad(datetime(2018, 3, 5))
