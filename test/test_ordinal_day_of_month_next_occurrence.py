"""A year-less "Nth day of <month>" names the same date as its digit form.

Ruling C reads a year-less day of a month as the next occurrence: the first
such day that is not before the anchor's day.  "15 march" and "the fifteenth
day of march" name one date, so they take one year.  An explicit year is kept
as written.  A part of a month ("early march", "the first week of march")
keeps the anchor's year, as ruling 1 reads it.

Gold years are worked by hand from the calendar.  At the anchor Sunday 22
November 2026, 15 March has passed, so the next one is 2027.  At the anchor
Tuesday 27 June 2017 it is 2018.  A day equal to the anchor's own day is that
day (22 November 2026, 27 June 2017).  The day before it is a year later.
29 February is the next leap year's: 2028 after the 2026 anchor, 2020 after
the 2017 anchor.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan

ANCHORS = {
    "a2026": datetime(2026, 11, 22, 9, 0),
    "a2017": datetime(2017, 6, 27, 13, 4),
}
NEXT_MARCH = {"a2026": 2027, "a2017": 2018}


def _start(text, lang, anchor):
    r = extract_timespan(text, lang, anchor)
    assert r is not None, f"{text!r} ({lang}) did not parse"
    return r.span.start


def _date(text, lang, anchor):
    s = _start(text, lang, anchor)
    return date(s.year, s.month, s.day)


# (lang, digit form, ordinal-day form), all for 15 March
FIFTEENTH_OF_MARCH = [
    ("en", "15 march", "the fifteenth day of march"),
    ("en", "march 15", "the 15th day of march"),
    ("es", "15 de marzo", "el decimoquinto día de marzo"),
    ("pt", "14 de março", "o décimo quarto dia de março"),
    ("pt", "15 de março", "o décimo quinto dia de março"),
    ("de", "15. März", "der fünfzehnte Tag im März"),
    ("de", "15. März", "der fünfzehnte Tag des März"),
    ("fr", "15 mars", "le quinzième jour de mars"),
    ("it", "15 marzo", "il quindicesimo giorno di marzo"),
    ("nl", "15 maart", "de vijftiende dag van maart"),
    ("ca", "15 de març", "el quinzè dia de març"),
    ("gl", "15 de marzo", "o décimo quinto día de marzo"),
]


@pytest.mark.parametrize("key", ANCHORS)
@pytest.mark.parametrize("lang,digit,ordinal", FIFTEENTH_OF_MARCH)
def test_ordinal_day_of_march_takes_next_year(lang, digit, ordinal, key):
    anchor = ANCHORS[key]
    day = 14 if "14" in digit else 15
    gold = date(NEXT_MARCH[key], 3, day)
    assert _date(digit, lang, anchor) == gold
    assert _date(ordinal, lang, anchor) == gold


@pytest.mark.parametrize("key", ANCHORS)
@pytest.mark.parametrize("lang,ordinal", [
    ("en", "the first day of march"),
    ("es", "el primer día de marzo"),
    ("pt", "o primeiro dia de março"),
    ("de", "der erste Tag im März"),
    ("fr", "le premier jour de mars"),
    ("it", "il primo giorno di marzo"),
    ("nl", "de eerste dag van maart"),
    ("ca", "el primer dia de març"),
    ("gl", "o primeiro día de marzo"),
])
def test_first_day_of_march_takes_next_year(lang, ordinal, key):
    assert _date(ordinal, lang, ANCHORS[key]) == date(NEXT_MARCH[key], 3, 1)


@pytest.mark.parametrize("lang,digit,ordinal", [
    ("en", "22 november", "the twenty-second day of november"),
    ("es", "22 de noviembre", "el vigésimo segundo día de noviembre"),
])
def test_day_equal_to_the_anchor_day_is_that_day(lang, digit, ordinal):
    anchor = ANCHORS["a2026"]
    assert _date(digit, lang, anchor) == date(2026, 11, 22)
    assert _date(ordinal, lang, anchor) == date(2026, 11, 22)


@pytest.mark.parametrize("lang,digit,ordinal,year", [
    ("en", "21 november", "the twenty-first day of november", 2027),
    ("en", "23 november", "the twenty-third day of november", 2026),
    ("en", "1 december", "the first day of december", 2026),
])
def test_neighbours_of_the_anchor_day(lang, digit, ordinal, year):
    anchor = ANCHORS["a2026"]
    assert _date(digit, lang, anchor).year == year
    assert _date(ordinal, lang, anchor).year == year


@pytest.mark.parametrize("lang,digit,ordinal,gold", [
    ("en", "27 june", "the twenty-seventh day of june", date(2017, 6, 27)),
    ("en", "26 june", "the twenty-sixth day of june", date(2018, 6, 26)),
    ("en", "28 june", "the twenty-eighth day of june", date(2017, 6, 28)),
])
def test_neighbours_of_the_2017_anchor_day(lang, digit, ordinal, gold):
    anchor = ANCHORS["a2017"]
    assert _date(digit, lang, anchor) == gold
    assert _date(ordinal, lang, anchor) == gold


@pytest.mark.parametrize("key,gold", [("a2026", date(2028, 2, 29)),
                                      ("a2017", date(2020, 2, 29))])
def test_leap_day_is_the_next_leap_year(key, gold):
    anchor = ANCHORS[key]
    assert _date("29 february", "en", anchor) == gold
    assert _date("the twenty-ninth day of february", "en", anchor) == gold


@pytest.mark.parametrize("text,lang,gold", [
    ("the fifteenth day of march 2026", "en", date(2026, 3, 15)),
    ("the fifteenth day of march 2030", "en", date(2030, 3, 15)),
    ("el decimoquinto día de marzo de 2026", "es", date(2026, 3, 15)),
])
def test_explicit_year_is_kept(text, lang, gold):
    assert _date(text, lang, ANCHORS["a2026"]) == gold


@pytest.mark.parametrize("text", [
    "early march",
    "the first week of march",
    "the middle of march",
])
def test_part_of_a_month_keeps_the_anchor_year(text):
    d = _date(text, "en", ANCHORS["a2026"])
    assert (d.year, d.month) == (2026, 3)
