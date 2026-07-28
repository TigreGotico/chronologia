# -*- coding: utf-8 -*-
"""Closed within-month range sweep (uk): "з D по E <month>(gen)".

«з ... по ...» names an inclusive period ending at the end of day E, so the
span is [D, E+1).  Months are held in the anchor's own future (July-December
2017) so the future-preference resolves unambiguously to 2017, and gold is pure
arithmetic on the named days.  Anchor Tue 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse

_MONTHS_GEN = {
    7: "липня", 8: "серпня", 9: "вересня",
    10: "жовтня", 11: "листопада", 12: "грудня",
}

_SPANS = ((3, 9), (5, 12), (10, 20), (1, 28), (14, 15), (2, 27))

_CASES = []
for _m, _gen in _MONTHS_GEN.items():
    for _d1, _d2 in _SPANS:
        _end = date(2017, _m, _d2) + timedelta(days=1)
        _CASES.append((f"з {_d1} по {_d2} {_gen}",
                       (2017, _m, _d1), (_end.year, _end.month, _end.day)))


@pytest.mark.parametrize("phrase,s,e", _CASES)
def test_closed_range(phrase, s, e):
    r = parse(phrase)
    assert r[0].start == AstroDate(*s), phrase
    assert r[0].end == AstroDate(*e), phrase
    assert r[1] == "", phrase
