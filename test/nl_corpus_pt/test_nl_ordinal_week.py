# -*- coding: utf-8 -*-
"""The "nth week of a month" reading of a weekday-homograph ordinal, pt.

Portuguese names its weekdays by ordinal -- "segunda(-feira)" is Monday and at
the same time the ordinal "second", "quarta" is Wednesday and the fourth, and
so on.  Those surfaces are withheld from the number fold so the weekday reading
survives, which left "a segunda semana de março" reading Monday instead of the
second week.  Directly before the week noun the weekday reading is impossible,
so the ordinal is licensed there; the weekday reading everywhere else must be
untouched.  Anchor 2017-06-27 (a terça).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, span, start_end, parse


@pytest.mark.parametrize("text,start,end", [
    ("a primeira semana de março", (2017, 3, 6), (2017, 3, 13)),
    ("a segunda semana de março", (2017, 3, 13), (2017, 3, 20)),
    ("a terceira semana de março", (2017, 3, 20), (2017, 3, 27)),
    ("a quarta semana de março", (2017, 3, 27), (2017, 4, 3)),
    ("a segunda semana de janeiro", (2017, 1, 9), (2017, 1, 16)),
    ("a quarta semana de janeiro", (2017, 1, 23), (2017, 1, 30)),
])
def test_nth_week_of_month(text, start, end):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == start
    assert (e.year, e.month, e.day) == end
    assert span(text).width.days == 7
    assert parse(text)[1] == ""


#: the first weekday of each name strictly at or after the terça anchor.
_NEXT = {
    "na segunda": (2017, 7, 3),        # Monday
    "na quarta": (2017, 6, 28),        # Wednesday
    "na quinta": (2017, 6, 29),        # Thursday
    "na sexta": (2017, 6, 30),         # Friday
    "na terça": (2017, 7, 4),          # Tuesday
    "segunda-feira": (2017, 7, 3),
    "quarta-feira": (2017, 6, 28),
    "quinta-feira": (2017, 6, 29),
    "sexta-feira": (2017, 6, 30),
}


@pytest.mark.parametrize("text,ymd", list(_NEXT.items()))
def test_weekday_reading_survives(text, ymd):
    """The homograph before no week noun is still the weekday it names."""
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == ymd
    assert s.width == timedelta(days=1)


def test_recurring_weekday_plural_untouched():
    """"todas as segundas-feiras" stays a Monday, never a second week."""
    s = span("todas as segundas-feiras")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 3)


@pytest.mark.parametrize("text", [
    "a segunda semana de",             # dangling scope, no month
    "semana de segunda de março",      # nonsense word order
    "segunda semana",                  # no month scope
])
def test_garbage_never_raises(text):
    parse(text)
