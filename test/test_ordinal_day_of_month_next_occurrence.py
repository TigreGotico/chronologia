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


# -- a range end with no year is its first occurrence on or after the start --

RANGE_ANCHORS = {"r2027": datetime(2027, 3, 3, 15, 30),
                 "r2026": datetime(2026, 11, 22, 9, 0)}
# the last day of February keeps the anchor's year, so it is 28 February of
# 2027 and of 2026; 10 March on or after it is 10 March of the same year
RANGE_START = {"r2027": date(2027, 2, 28), "r2026": date(2026, 2, 28)}

RANGES_TO_THE_TENTH = [
    ("en", "from the last day of february to 10 march"),
    ("en", "from the last day of february to the 10th day of march"),
    ("en", "from early march to 10 march"),
    ("en", "from early march to the 10th day of march"),
    ("es", "del último día de febrero al 10 de marzo"),
    ("es", "del último día de febrero al décimo día de marzo"),
    ("pt", "do último dia de fevereiro a 10 de março"),
    ("pt", "do último dia de fevereiro ao décimo dia de março"),
    ("de", "vom letzten Tag im Februar bis zum 10. März"),
    ("de", "vom letzten Tag im Februar bis zum zehnten Tag im März"),
    ("fr", "du dernier jour de février au 10 mars"),
    ("fr", "du dernier jour de février au dixième jour de mars"),
]


@pytest.mark.parametrize("key", RANGE_ANCHORS)
@pytest.mark.parametrize("lang,text", RANGES_TO_THE_TENTH)
def test_range_end_is_first_occurrence_after_the_start(lang, text, key):
    r = extract_timespan(text, lang, RANGE_ANCHORS[key])
    assert r is not None, f"{text!r} ({lang}) did not parse"
    year = RANGE_START[key].year
    end = r.span.end
    assert (end.year, end.month, end.day) == (year, 3, 11)
    start = r.span.start
    first = (date(year, 3, 1) if "early" in text else RANGE_START[key])
    assert (start.year, start.month, start.day) == (first.year, first.month,
                                                    first.day)


@pytest.mark.parametrize("key", RANGE_ANCHORS)
@pytest.mark.parametrize("text", [
    "from the last day of february to 1 march",
    "from the last day of february to the first day of march",
])
def test_range_to_the_first_of_march_ends_on_the_second(text, key):
    r = extract_timespan(text, "en", RANGE_ANCHORS[key])
    year = RANGE_START[key].year
    assert (r.span.start.year, r.span.start.month, r.span.start.day) \
        == (year, 2, 28)
    assert (r.span.end.year, r.span.end.month, r.span.end.day) \
        == (year, 3, 2)


def test_range_of_two_dates_keeps_its_cycle():
    # both ends roll to the next occurrence together: 10 and 20 March 2027
    r = extract_timespan("from 10 march to 20 march", "en", ANCHORS["a2026"])
    assert (r.span.start.year, r.span.start.month, r.span.start.day) \
        == (2027, 3, 10)
    assert (r.span.end.year, r.span.end.month, r.span.end.day) \
        == (2027, 3, 21)


# -- forms that keep the anchor's year ---------------------------------------

@pytest.mark.parametrize("key", ANCHORS)
@pytest.mark.parametrize("lang,text", [
    ("en", "the last day of march"),
    ("es", "el último día de marzo"),
])
def test_last_day_of_march_keeps_the_anchor_year(lang, text, key):
    anchor = ANCHORS[key]
    assert _date(text, lang, anchor) == date(anchor.year, 3, 31)


@pytest.mark.parametrize("text", [
    "the 0th day of march",
    "the 32nd day of march",
    "the 31st day of april",
])
def test_a_day_no_month_holds_is_refused(text):
    assert extract_timespan(text, "en", ANCHORS["a2026"]) is None


# -- a range said inside itself, across the new year or 29 February ----------

# said on 20 December 2026 the start is 1 December 2026 and the end the
# 10 January of 2027; said on 31 December 2027 the same range ends in 2028
NEW_YEAR_RANGES = [
    ("en", "from the 1st day of december to 10 january"),
    ("en", "from 1 december to 10 january"),
    ("es", "del primer día de diciembre al 10 de enero"),
    ("es", "del 1 de diciembre al 10 de enero"),
    ("pt", "do primeiro dia de dezembro a 10 de janeiro"),
    ("pt", "de 1 de dezembro a 10 de janeiro"),
    ("de", "vom ersten Tag im Dezember bis zum 10. Januar"),
    ("de", "vom 1. Dezember bis zum 10. Januar"),
    ("fr", "du premier jour de décembre au 10 janvier"),
    ("fr", "du 1 décembre au 10 janvier"),
]


@pytest.mark.parametrize("anchor,year", [(datetime(2026, 12, 20, 9, 0), 2026),
                                         (datetime(2027, 12, 31, 9, 0), 2027)])
@pytest.mark.parametrize("lang,text", NEW_YEAR_RANGES)
def test_range_across_the_new_year_holds_the_anchor(lang, text, anchor, year):
    r = extract_timespan(text, lang, anchor)
    assert r is not None, f"{text!r} ({lang}) did not parse"
    assert r.remainder == ""
    s, e = r.span.start, r.span.end
    assert (s.year, s.month, s.day) == (year, 12, 1)
    assert (e.year, e.month, e.day) == (year + 1, 1, 11)


@pytest.mark.parametrize("lang,text", [
    ("en", "from the 29th day of february to the 1st day of march"),
    ("en", "from 29 february to 1 march"),
    ("es", "del 29 de febrero al 1 de marzo"),
    ("pt", "de 29 de fevereiro a 1 de março"),
    ("de", "vom 29. Februar bis zum 1. März"),
    ("fr", "du 29 février au 1 mars"),
])
def test_range_from_the_leap_day_said_on_the_first_of_march(lang, text):
    r = extract_timespan(text, lang, datetime(2028, 3, 1, 9, 0))
    assert r is not None, f"{text!r} ({lang}) did not parse"
    s, e = r.span.start, r.span.end
    assert (s.year, s.month, s.day) == (2028, 2, 29)
    assert (e.year, e.month, e.day) == (2028, 3, 2)


@pytest.mark.parametrize("text", ["from 12 june to 5 june",
                                  "from the 12th day of june to 5 june"])
def test_a_reversed_range_is_still_refused(text):
    r = extract_timespan(text, "en", datetime(2017, 6, 27, 13, 4))
    assert r is None or r.remainder != ""
