"""Weekday names, and the single-syllable abbreviations this locale refuses."""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, day, nomatch, parse, start_end

#: the anchor is a Wednesday, so the next occurrence of each weekday is
#: computed here rather than read back from the parser.
_NEXT = {
    "월요일": 0, "화요일": 1, "수요일": 2, "목요일": 3, "금요일": 4,
    "토요일": 5, "일요일": 6,
}


def _next_occurrence(index):
    d = ANCHOR + timedelta(days=1)
    while d.weekday() != index:
        d += timedelta(days=1)
    return d


@pytest.mark.parametrize("name,index", sorted(_NEXT.items()))
def test_a_bare_weekday_names_its_next_occurrence(name, index):
    d = _next_occurrence(index)
    assert start_end(name) == day(d.year, d.month, d.day)


@pytest.mark.parametrize("name,index", sorted(_NEXT.items()))
def test_the_weekday_series_is_indexed_from_monday(name, index):
    d = _next_occurrence(index)
    assert datetime(d.year, d.month, d.day).weekday() == index


@pytest.mark.parametrize("text,expected", [
    ("지난 금요일", datetime(2027, 5, 7)),
    ("다음 금요일", datetime(2027, 5, 14)),
    ("지난 월요일", datetime(2027, 5, 10)),
    ("다음 수요일", datetime(2027, 5, 19)),
])
def test_a_marked_weekday(text, expected):
    assert start_end(text) == day(expected.year, expected.month, expected.day)


@pytest.mark.parametrize("text", ["일", "월", "화", "수", "목", "금", "토"])
def test_the_single_syllable_abbreviations_name_no_weekday(text):
    """CLDR abbreviates the weekdays to one syllable each, and every one of
    those syllables is an ordinary word: 일 is the day, the numeral one and
    Sunday at once; 월 is the month and Monday; 수 is a number and water; 금
    is gold.  Nothing inside a phrase separates the readings -- only the
    column of a calendar grid does, and a grid is not prose.  So the
    abbreviations are not shipped, and a bare one names nothing rather than
    naming whichever reading happened to be listed first."""
    nomatch(text)


@pytest.mark.parametrize("text,weekday", [("지난 일", 6), ("다음 월", 0)])
def test_a_marked_abbreviation_still_names_no_weekday(text, weekday):
    """The refusal holds under a determiner as well.  지난 일 does resolve,
    but as "the last day" -- 일 read as the day UNIT, the reading the
    determiner licenses -- and never as last Sunday; 다음 월 resolves to
    nothing at all, because the month word here is 달."""
    r = parse(text)
    if r is not None:
        got = datetime(r[0].start.year, r[0].start.month, r[0].start.day)
        assert got.weekday() != weekday
