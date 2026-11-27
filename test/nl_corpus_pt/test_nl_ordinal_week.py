# -*- coding: utf-8 -*-
"""The "nth week of a month" reading of a weekday-homograph ordinal, pt.

Portuguese names its weekdays by ordinal -- "segunda(-feira)" is Monday and at
the same time the ordinal "second", "quarta" is Wednesday and the fourth, and
so on.  Those surfaces are withheld from the number fold so the weekday reading
survives, which left "a segunda semana de março" reading Monday instead of the
second week.  Directly before the week noun the weekday reading is impossible,
so the ordinal is licensed there; the weekday reading everywhere else must be
untouched.  Anchor 2017-06-27 (a terça).

Ruling 1 (changed on 26 November 2026): a part of a month with no year takes
the year the month alone takes, so março and janeiro (ended at the anchor) are
2018, where week 1 starts on the first Monday (5 March, 1 January).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, span, start_end, parse


@pytest.mark.parametrize("text,start,end", [
    # ruling 1: março and janeiro have ended at the anchor, so they are 2018
    ("a primeira semana de março", (2018, 3, 5), (2018, 3, 12)),
    ("a segunda semana de março", (2018, 3, 12), (2018, 3, 19)),
    ("a terceira semana de março", (2018, 3, 19), (2018, 3, 26)),
    ("a quarta semana de março", (2018, 3, 26), (2018, 4, 2)),
    ("a segunda semana de janeiro", (2018, 1, 8), (2018, 1, 15)),
    ("a quarta semana de janeiro", (2018, 1, 22), (2018, 1, 29)),
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
    "na terça": (2017, 6, 27),         # Tuesday, the anchor day
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
