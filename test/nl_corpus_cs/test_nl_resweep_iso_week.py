# -*- coding: utf-8 -*-
"""Second-pass sweep: ISO-8601 weeks (cs), Monday-based, across 15 fresh
(year, week) combos not used by test_nl_iso_week.py. Mondays computed with
stdlib date.fromisocalendar -- never the parser."""
import pytest
from ._corpus import AstroDate, start_end


CASES = [
    ('týden 1 2033', (2033, 1, 3, 0, 0), (2033, 1, 10, 0, 0)),
    ('týden 20 2033', (2033, 5, 16, 0, 0), (2033, 5, 23, 0, 0)),
    ('týden 52 2033', (2033, 12, 26, 0, 0), (2034, 1, 2, 0, 0)),
    ('týden 15 2036', (2036, 4, 7, 0, 0), (2036, 4, 14, 0, 0)),
    ('týden 33 2036', (2036, 8, 11, 0, 0), (2036, 8, 18, 0, 0)),
    ('týden 9 2040', (2040, 2, 27, 0, 0), (2040, 3, 5, 0, 0)),
    ('týden 44 2040', (2040, 10, 29, 0, 0), (2040, 11, 5, 0, 0)),
    ('týden 27 2044', (2044, 7, 4, 0, 0), (2044, 7, 11, 0, 0)),
    ('týden 51 2044', (2044, 12, 19, 0, 0), (2044, 12, 26, 0, 0)),
    ('týden 6 2048', (2048, 2, 3, 0, 0), (2048, 2, 10, 0, 0)),
    ('týden 40 2048', (2048, 9, 28, 0, 0), (2048, 10, 5, 0, 0)),
    ('týden 12 1988', (1988, 3, 21, 0, 0), (1988, 3, 28, 0, 0)),
    ('týden 46 1988', (1988, 11, 14, 0, 0), (1988, 11, 21, 0, 0)),
    ('týden 18 2002', (2002, 4, 29, 0, 0), (2002, 5, 6, 0, 0)),
    ('týden 39 2002', (2002, 9, 23, 0, 0), (2002, 9, 30, 0, 0)),
]


@pytest.mark.parametrize("text,s,e", CASES)
def test_span(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))
