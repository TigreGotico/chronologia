# -*- coding: utf-8 -*-
"""A 24-hour clock with the pm marker 오후, ko.

오후 is the pm half of the day, "낮 열두 시부터 밤 열두 시까지의 시간"
(표준국어대사전, s.v. 오후 2 (午後) 「1」, https://stdict.korean.go.kr), so
a later 24-hour clock keeps its hour:
"오후 19:30" is 19:30, as "오후 7:30" is.  An afternoon or evening marker
never holds midnight, so "오후 00:30" names no time.
Anchor: Wednesday 2027-05-12 13:04.
"""
from datetime import datetime

import pytest

from ._corpus import ad, nomatch, start


@pytest.mark.parametrize("text,expected", [
    ("오후 19:30", datetime(2027, 5, 12, 19, 30)),
    ("오후 22:00", datetime(2027, 5, 12, 22, 0)),
])
def test_the_pm_marker_keeps_a_later_clock(text, expected):
    assert start(text) == ad(expected)


def test_the_pm_marker_holds_no_midnight():
    nomatch("오후 00:30")
