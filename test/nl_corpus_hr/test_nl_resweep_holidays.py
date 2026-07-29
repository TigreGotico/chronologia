# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: Croatian public holidays with an explicit year, fresh
years not touched by test_nl_holiday_ref (which only covers the bare form
plus "uskrs 2020"/"nova godina 2020").

Croatian public holidays registered in chronologia/holiday_data/hr.tab:
Nova godina (1/1), Bogojavljenje ili Sveta tri kralja (1/6), Praznik rada
(5/1), Dan državnosti (5/30), Dan antifašističke borbe (6/22), Dan pobjede i
domovinske zahvalnosti i Dan hrvatskih branitelja (8/5), Velika Gospa (8/15),
Svi sveti (11/1), Božić (12/25), Sveti Stjepan (12/26).

PROBED first: "nova godina", "sveta tri kralja", "svi sveti" and "božić"
resolve correctly with an explicit trailing year.  The other six degrade to
a bare-year span (the holiday text is dropped and only the year is folded,
resolving to <year>-01-01) -- these are STRICT xfails carrying the CORRECT
gold (the calendar date, independent of the parser) per instructions.

Anchor Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import AstroDate, start

_YEARS = (2011, 2012, 2013, 2014, 2015, 2016, 2019, 2022, 2023, 2024, 2025,
          2026, 2027, 2028, 2029, 2031, 2033, 2035, 2040, 2045)

_WORKING = [
    ('nova godina', 1, 1),
    ('sveta tri kralja', 1, 6),
    ('svi sveti', 11, 1),
    ('božić', 12, 25),
]

_DEGRADED = [
    ('praznik rada', 5, 1),
    ('dan državnosti', 5, 30),
    ('dan antifašističke borbe', 6, 22),
    ('dan pobjede', 8, 5),
    ('velika gospa', 8, 15),
    ('sveti stjepan', 12, 26),
]

_WORKING_CASES = [(f"{name} {y}", y, mm, dd)
                   for name, mm, dd in _WORKING for y in _YEARS]


@pytest.mark.parametrize("phrase,y,mm,dd", _WORKING_CASES,
                          ids=[c[0] for c in _WORKING_CASES])
def test_holiday_explicit_year_resweep(phrase, y, mm, dd):
    assert start(phrase) == AstroDate(y, mm, dd), phrase


_DEGRADED_CASES = [(f"{name} {y}", y, mm, dd)
                    for name, mm, dd in _DEGRADED for y in _YEARS]


@pytest.mark.xfail(strict=True, reason=(
    "hr: explicit-year holiday form drops the holiday text and folds to a "
    "bare-year span (<year>-01-01) instead of the holiday's fixed date; "
    "gold is the correct holiday date, never the parser's degraded output"))
@pytest.mark.parametrize("phrase,y,mm,dd", _DEGRADED_CASES,
                          ids=[c[0] for c in _DEGRADED_CASES])
def test_holiday_explicit_year_degrades_resweep(phrase, y, mm, dd):
    assert start(phrase) == AstroDate(y, mm, dd), phrase
