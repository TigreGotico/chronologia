# -*- coding: utf-8 -*-
"""Month-third sweep (uk): початок/середина/кінець <month>(gen) = the first/
middle/last arithmetic third of the named calendar month.

The parent month runs from its first day to the first of the next month; the
third is pure ``timedelta`` arithmetic ((parent)/3) that never touches the
parser.  Bare month names bind to the anchor year (2017).  Anchor Tue
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
    _ms = datetime(_Y, _m, 1)
    _me = datetime(_Y + 1, 1, 1) if _m == 12 else datetime(_Y, _m + 1, 1)
    for _word, _part in _PARTS.items():
        _CASES.append((f"{_word} {_MONTHS_GEN[_m]}", _third(_ms, _me, _part)))


@pytest.mark.parametrize("phrase,gold", _CASES)
def test_month_third(phrase, gold):
    assert start_end(phrase) == gold, phrase
