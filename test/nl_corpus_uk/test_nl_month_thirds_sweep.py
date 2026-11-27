# -*- coding: utf-8 -*-
"""Month-third sweep (uk): початок/середина/кінець <month>(gen) = the first/
middle/last arithmetic third of the named calendar month.

The parent month runs from its first day to the first of the next month; the
third is pure ``timedelta`` arithmetic ((parent)/3) that never touches the
parser.  A bare month name takes the year the month alone takes
(ruling 1, changed 26 November 2026): 2018 for January to May, 2017 for June
to December.  Anchor Tue
2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from ._corpus import AstroDate, start_end

_MONTHS_GEN = [
    None, "січня", "лютого", "березня", "квітня", "травня", "червня",
    "липня", "серпня", "вересня", "жовтня", "листопада", "грудня",
]

_PARTS = {"початок": "early", "середина": "mid", "кінець": "late"}

_Y = 2017


def _third(s, e, part):
    w = (e - s) / 3
    edges = {"early": (s, s + w), "mid": (s + w, s + 2 * w),
             "late": (s + 2 * w, e)}[part]
    return (AstroDate.from_datetime(edges[0]),
            AstroDate.from_datetime(edges[1]))


_CASES = []
for _m in range(1, 13):
    # ruling 1 (changed 26 November 2026): a part of a month takes its month's year; a month that has ended at the anchor is next year's
    _y = _Y + (_m < 6)
    _ms = datetime(_y, _m, 1)
    _me = datetime(_y + 1, 1, 1) if _m == 12 else datetime(_y, _m + 1, 1)
    for _word, _part in _PARTS.items():
        _CASES.append((f"{_word} {_MONTHS_GEN[_m]}", _third(_ms, _me, _part)))


@pytest.mark.parametrize("phrase,gold", _CASES)
def test_month_third(phrase, gold):
    assert start_end(phrase) == gold, phrase
