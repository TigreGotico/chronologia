"""A part of a month follows its month's year (ruling 1).

A month named without a day is its next occurrence as a span: the month that
holds the anchor is this one, a month that has ended is next year's.  A part
of that month ("early january", "the first week of january", "the last day of
january", "the first half of january") names a span inside the month, so it
takes the month's year.  An explicit year wins.  A year phrase after the month
("janvier dernier", "january next year") names the month's year as the bare
month reads it, and the part takes that year too.

Gold values are worked by hand from the calendar, never read from chronologia.
The main anchor is Thursday 26 November 2026, 10:00.  January 2026 has ended,
so January is January 2027.  1 January 2027 is a Friday (26 November 2026 is a
Thursday, so 31 December 2026 is a Thursday too).  The Mondays of January 2027
are the 4th, 11th, 18th and 25th, and its Saturdays are the 2nd, 9th, 16th,
23rd and 30th.  A week of a month starts on its first Monday (ruling 14), so
the first week of January 2027 is 4 to 11 January.  The locale weekend starts
on Saturday, so the first weekend is 2 to 4 January.

January has 31 days.  A third is 10 days 8 hours, so early January runs to
11 January 08:00 and late January starts on 21 January 16:00.  A half is
15 days 12 hours, and a quarter is 7 days 18 hours.

December 2026 has not started and November 2026 holds the anchor, so both
stay in 2026: late December is 21 December 16:00 to 1 January 2027, early
November is 1 to 11 November (a 30-day month, thirds of 10 days), the first
Monday of November 2026 is the 2nd (1 November 2026 is a Sunday), and the
first week of December 2026 starts on Monday 7 December (1 December is a
Tuesday).
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

A = datetime(2026, 11, 26, 10, 0)

JAN = datetime(2027, 1, 1)
THIRD = timedelta(days=31) / 3          # 10 days 8 hours
HALF = timedelta(days=31) / 2           # 15 days 12 hours
QUARTER = timedelta(days=31) / 4        # 7 days 18 hours
FEB = datetime(2027, 2, 1)

EARLY_JAN = (JAN, JAN + THIRD)
MID_JAN = (JAN + THIRD, JAN + 2 * THIRD)
LATE_JAN = (JAN + 2 * THIRD, FEB)
FIRST_WEEK_JAN = (datetime(2027, 1, 4), datetime(2027, 1, 11))
FIRST_MONDAY_JAN = (datetime(2027, 1, 4), datetime(2027, 1, 5))
LAST_MONDAY_JAN = (datetime(2027, 1, 25), datetime(2027, 1, 26))
LAST_DAY_JAN = (datetime(2027, 1, 31), FEB)
FIRST_WEEKEND_JAN = (datetime(2027, 1, 2), datetime(2027, 1, 4))
LAST_WEEKEND_JAN = (datetime(2027, 1, 30), datetime(2027, 2, 1))
FIRST_HALF_JAN = (JAN, JAN + HALF)
SECOND_HALF_JAN = (JAN + HALF, FEB)
FIRST_QUARTER_JAN = (JAN, JAN + QUARTER)
LAST_QUARTER_JAN = (FEB - QUARTER, FEB)


def _span(text, lang, anchor=A):
    r = extract_timespan(text, lang, anchor)
    assert r is not None, f"{text!r} ({lang}) did not parse"
    assert r.remainder == "", f"{text!r} ({lang}) left {r.remainder!r}"
    return r.span.start_datetime, r.span.end_datetime


# -- a part of a month that has ended is next year's ---------------------------

PARTS_OF_JANUARY = [
    # early / mid / late (month_fuzzy)
    ("en", "early january", EARLY_JAN),
    ("en", "the beginning of january", EARLY_JAN),
    ("en", "the middle of january", MID_JAN),
    ("en", "late january", LATE_JAN),
    ("en", "the end of january", LATE_JAN),
    ("fr", "début janvier", EARLY_JAN),
    ("fr", "au début de janvier", EARLY_JAN),
    ("fr", "mi-janvier", MID_JAN),
    ("fr", "fin janvier", LATE_JAN),
    ("pt", "início de janeiro", EARLY_JAN),
    ("pt", "no início de janeiro", EARLY_JAN),
    ("pt", "meados de janeiro", MID_JAN),
    ("pt", "fim de janeiro", LATE_JAN),
    ("es", "principios de enero", EARLY_JAN),
    ("es", "a principios de enero", EARLY_JAN),
    ("es", "mediados de enero", MID_JAN),
    ("es", "finales de enero", LATE_JAN),
    ("de", "Anfang Januar", EARLY_JAN),
    ("de", "Mitte Januar", MID_JAN),
    ("de", "Ende Januar", LATE_JAN),
    ("it", "inizio gennaio", EARLY_JAN),
    ("it", "fine gennaio", LATE_JAN),
    ("nl", "begin januari", EARLY_JAN),
    ("nl", "eind januari", LATE_JAN),
    ("ca", "principis de gener", EARLY_JAN),
    # the n-th week of the month (scoped_ordinal)
    ("en", "the first week of january", FIRST_WEEK_JAN),
    ("fr", "la première semaine de janvier", FIRST_WEEK_JAN),
    ("pt", "a primeira semana de janeiro", FIRST_WEEK_JAN),
    ("es", "la primera semana de enero", FIRST_WEEK_JAN),
    ("de", "die erste Woche im Januar", FIRST_WEEK_JAN),
    ("it", "la prima settimana di gennaio", FIRST_WEEK_JAN),
    ("nl", "de eerste week van januari", FIRST_WEEK_JAN),
    ("ca", "la primera setmana de gener", FIRST_WEEK_JAN),
    # the n-th or last weekday of the month (scoped_ordinal)
    ("en", "the first monday of january", FIRST_MONDAY_JAN),
    ("en", "the last monday of january", LAST_MONDAY_JAN),
    ("fr", "le premier lundi de janvier", FIRST_MONDAY_JAN),
    ("pt", "a primeira segunda-feira de janeiro", FIRST_MONDAY_JAN),
    ("es", "el primer lunes de enero", FIRST_MONDAY_JAN),
    ("de", "der erste Montag im Januar", FIRST_MONDAY_JAN),
    ("it", "il primo lunedì di gennaio", FIRST_MONDAY_JAN),
    ("nl", "de eerste maandag van januari", FIRST_MONDAY_JAN),
    ("ca", "el primer dilluns de gener", FIRST_MONDAY_JAN),
    # the last day of the month: a day with no number (scoped_ordinal)
    ("en", "the last day of january", LAST_DAY_JAN),
    ("fr", "le dernier jour de janvier", LAST_DAY_JAN),
    ("pt", "o último dia de janeiro", LAST_DAY_JAN),
    ("es", "el último día de enero", LAST_DAY_JAN),
    ("de", "der letzte Tag im Januar", LAST_DAY_JAN),
    ("it", "l'ultimo giorno di gennaio", LAST_DAY_JAN),
    ("nl", "de laatste dag van januari", LAST_DAY_JAN),
    # the n-th weekend of the month (weekend_of_month)
    ("en", "the first weekend of january", FIRST_WEEKEND_JAN),
    ("en", "the last weekend of january", LAST_WEEKEND_JAN),
    ("fr", "le premier week-end de janvier", FIRST_WEEKEND_JAN),
    ("pt", "o primeiro fim de semana de janeiro", FIRST_WEEKEND_JAN),
    ("es", "el primer fin de semana de enero", FIRST_WEEKEND_JAN),
    ("de", "das erste Wochenende im Januar", FIRST_WEEKEND_JAN),
    ("it", "il primo fine settimana di gennaio", FIRST_WEEKEND_JAN),
    ("nl", "het eerste weekend van januari", FIRST_WEEKEND_JAN),
    # a half or a quarter of the month (half_period, quarter_of_month)
    ("en", "the first half of january", FIRST_HALF_JAN),
    ("en", "the second half of january", SECOND_HALF_JAN),
    ("fr", "la première moitié de janvier", FIRST_HALF_JAN),
    ("pt", "a primeira metade de janeiro", FIRST_HALF_JAN),
    ("es", "la primera mitad de enero", FIRST_HALF_JAN),
    ("it", "la prima metà di gennaio", FIRST_HALF_JAN),
    ("nl", "de eerste helft van januari", FIRST_HALF_JAN),
    ("ca", "la primera meitat de gener", FIRST_HALF_JAN),
    ("en", "the first quarter of january", FIRST_QUARTER_JAN),
    ("en", "the last quarter of january", LAST_QUARTER_JAN),
]


@pytest.mark.parametrize("lang,text,gold", PARTS_OF_JANUARY)
def test_a_part_of_a_month_that_has_ended_is_next_years(lang, text, gold):
    assert _span(text, lang) == gold


# the bare month and the dated first day agree with the parts: January 2027
@pytest.mark.parametrize("lang,month,first_day", [
    ("en", "january", "the 1st of january"),
    ("fr", "janvier", "le 1er janvier"),
    ("pt", "janeiro", "1 de janeiro"),
    ("es", "enero", "1 de enero"),
    ("de", "Januar", "1. Januar"),
])
def test_the_bare_month_and_its_first_day_are_next_year(lang, month,
                                                        first_day):
    assert _span(month, lang) == (JAN, FEB)
    assert _span(first_day, lang) == (JAN, datetime(2027, 1, 2))


# -- the month that holds the anchor and a month still ahead stay -------------

LATE_DEC = (datetime(2026, 12, 1) + 2 * THIRD, datetime(2027, 1, 1))
EARLY_NOV = (datetime(2026, 11, 1), datetime(2026, 11, 11))


@pytest.mark.parametrize("lang,text,gold", [
    ("en", "late december", LATE_DEC),
    ("fr", "fin décembre", LATE_DEC),
    ("pt", "final de dezembro", LATE_DEC),
    ("es", "finales de diciembre", LATE_DEC),
    ("de", "Ende Dezember", LATE_DEC),
    ("en", "the first week of december",
     (datetime(2026, 12, 7), datetime(2026, 12, 14))),
    ("fr", "la première semaine de décembre",
     (datetime(2026, 12, 7), datetime(2026, 12, 14))),
    # November holds the anchor: it is this November, as "november" is,
    # even where the part has already passed
    ("en", "early november", EARLY_NOV),
    ("fr", "début novembre", EARLY_NOV),
    ("pt", "início de novembro", EARLY_NOV),
    ("es", "principios de noviembre", EARLY_NOV),
    ("de", "Anfang November", EARLY_NOV),
    ("en", "the first monday of november",
     (datetime(2026, 11, 2), datetime(2026, 11, 3))),
    ("es", "el primer lunes de noviembre",
     (datetime(2026, 11, 2), datetime(2026, 11, 3))),
    ("en", "the last day of november",
     (datetime(2026, 11, 30), datetime(2026, 12, 1))),
    ("fr", "le dernier jour de novembre",
     (datetime(2026, 11, 30), datetime(2026, 12, 1))),
])
def test_this_month_and_a_month_ahead_keep_the_anchor_year(lang, text, gold):
    assert _span(text, lang) == gold


# -- an explicit year wins -----------------------------------------------------

EARLY_JAN_2026 = (datetime(2026, 1, 1), datetime(2026, 1, 1) + THIRD)


@pytest.mark.parametrize("lang,text", [
    ("en", "early january 2026"),
    ("fr", "début janvier 2026"),
    ("pt", "início de janeiro de 2026"),
    ("de", "Anfang Januar 2026"),
])
def test_an_explicit_year_wins(lang, text):
    assert _span(text, lang) == EARLY_JAN_2026


# -- a year phrase after the month: the part takes the bare month's year ------

LATE_JAN_2026 = (datetime(2026, 1, 1) + 2 * THIRD, datetime(2026, 2, 1))
LATE_JAN_2025 = (datetime(2025, 1, 1) + 2 * THIRD, datetime(2025, 2, 1))


@pytest.mark.parametrize("lang,text,gold", [
    # "janvier dernier" is the latest January that has ended: January 2026
    ("fr", "fin janvier dernier", LATE_JAN_2026),
    ("es", "finales de enero pasado", LATE_JAN_2026),
    ("pt", "final de janeiro passado", LATE_JAN_2026),
    # "last year" names 2025
    ("en", "late january last year", LATE_JAN_2025),
    ("de", "Ende Januar letzten Jahres", LATE_JAN_2025),
    # "prochain" and "next year" name January 2027
    ("fr", "début janvier prochain", EARLY_JAN),
    ("es", "principios de enero del año que viene", EARLY_JAN),
    ("en", "the first week of january next year", FIRST_WEEK_JAN),
    # 1 January 2025 is a Wednesday, so the first Saturday is the 4th
    ("pt", "o primeiro fim de semana de janeiro do ano passado",
     (datetime(2025, 1, 4), datetime(2025, 1, 6))),
])
def test_a_year_phrase_after_the_month_names_the_parts_year(lang, text, gold):
    assert _span(text, lang) == gold


# -- "since": the part that has begun, as "since october" reads it ------------

@pytest.mark.parametrize("lang,text", [
    ("en", "since early october"),
    ("fr", "depuis début octobre"),
    ("pt", "desde o início de outubro"),
    ("es", "desde principios de octubre"),
    ("de", "seit Anfang Oktober"),
])
def test_since_a_part_of_a_month_reads_back(lang, text):
    assert _span(text, lang) == (datetime(2026, 10, 1), A)


# the first Monday of January 2026 is the 5th (1 January 2026 is a Thursday),
# the last is the 26th; February 2026 has 28 days.  A weekday of a named month
# is read back a year, not a week ("since monday" reads a week back)
@pytest.mark.parametrize("lang,text,start", [
    ("en", "since the first monday of january", datetime(2026, 1, 5)),
    ("en", "since the last monday of january", datetime(2026, 1, 26)),
    ("fr", "depuis le dernier lundi de janvier", datetime(2026, 1, 26)),
    ("en", "since the last day of february", datetime(2026, 2, 28)),
    ("es", "desde el último día de febrero", datetime(2026, 2, 28)),
    ("de", "seit dem letzten Tag im Februar", datetime(2026, 2, 28)),
])
def test_since_a_day_of_a_named_month_reads_back_a_year(lang, text, start):
    assert _span(text, lang) == (start, A)


# -- ranges ----------------------------------------------------------------

def test_a_range_of_two_parts_after_the_new_year():
    # both months have ended this year, so both are 2027's
    assert _span("from early january to late february", "en") \
        == (JAN, datetime(2027, 3, 1))


def test_a_range_that_holds_the_anchor_stays():
    # late October 2026 to early December 2026 holds the anchor; October
    # 2026 starts 21 October 16:00 (31 days), December's early third ends on
    # 11 December 08:00
    oct1, dec1 = datetime(2026, 10, 1), datetime(2026, 12, 1)
    assert _span("from late october to early december", "en") \
        == (oct1 + 2 * THIRD, dec1 + THIRD)


def test_a_range_across_the_new_year():
    # early December 2026 to late January 2027
    assert _span("from early december to late january", "en") \
        == (datetime(2026, 12, 1), FEB)


@pytest.mark.parametrize("lang,text", [
    ("en", "from the last day of february to 10 march"),
    ("es", "del último día de febrero al 10 de marzo"),
    ("de", "vom letzten Tag im Februar bis zum 10. März"),
])
def test_a_range_from_a_last_day_that_holds_the_anchor(lang, text):
    # said on 3 March 2027, February 2027 has ended, so the last day of
    # February alone is 29 February 2028.  The range to 10 March holds the
    # anchor from 28 February 2027, as "from february to march" does: the
    # ordinal "last" is no "last" marker, so the start is pulled back a year
    anchor = datetime(2027, 3, 3, 15, 30)
    assert _span(text, lang, anchor) \
        == (datetime(2027, 2, 28), datetime(2027, 3, 11))


# -- other anchors -----------------------------------------------------------

@pytest.mark.parametrize("anchor,lang,text,gold", [
    # said on New Year's Eve 2026: January is 2027, December is this one
    (datetime(2026, 12, 31, 9, 0), "en", "early january", EARLY_JAN),
    (datetime(2026, 12, 31, 9, 0), "fr", "fin décembre", LATE_DEC),
    # said on 15 January 2027: January holds the anchor; December 2026 has
    # ended, so December is December 2027
    (datetime(2027, 1, 15, 9, 0), "pt", "fim de janeiro", LATE_JAN),
    (datetime(2027, 1, 15, 9, 0), "es", "principios de diciembre",
     (datetime(2027, 12, 1), datetime(2027, 12, 1) + THIRD)),
    # said on 27 June 2017: March 2017 has ended, so the last day of March
    # is 31 March 2018
    (datetime(2017, 6, 27, 13, 4), "en", "the last day of march",
     (datetime(2018, 3, 31), datetime(2018, 4, 1))),
    (datetime(2017, 6, 27, 13, 4), "es", "el último día de marzo",
     (datetime(2018, 3, 31), datetime(2018, 4, 1))),
])
def test_other_anchors(anchor, lang, text, gold):
    assert _span(text, lang, anchor) == gold
