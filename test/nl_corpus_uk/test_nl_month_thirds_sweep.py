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
    for _word, _part in _PARTS.items():
        _y = _Y + (_m < 6)
        # ruling 1 (26 November 2026): a part of a month is read as a span; a
        # part of the anchor's own month that has ended at 2017-06-27 13:04
        # (початок, середина of June) is June 2018, the part that holds it
        # (кінець) stays 2017
        if _m == 6:
            _s0, _e0 = datetime(_y, _m, 1), datetime(_y, _m + 1, 1)
            _w0 = (_e0 - _s0) / 3
            _end0 = {"early": _s0 + _w0, "mid": _s0 + 2 * _w0, "late": _e0}[_part]
            if _end0 <= datetime(2017, 6, 27, 13, 4):
                _y += 1
        _ms = datetime(_y, _m, 1)
        _me = datetime(_y + 1, 1, 1) if _m == 12 else datetime(_y, _m + 1, 1)
        _CASES.append((f"{_word} {_MONTHS_GEN[_m]}", _third(_ms, _me, _part)))


@pytest.mark.parametrize("phrase,gold", _CASES)
def test_month_third(phrase, gold):
    assert start_end(phrase) == gold, phrase
