"""A day, weekday or week "of the month" that has passed is next month's, en.

A named occurrence is the next one after the anchor, and a span that ended
before the anchor names the next such span.  "of this month" names the
anchor's own month and never rolls.

Anchor Saturday 2026-10-17 12:00.  October 2026 starts on a Thursday (first
Tuesday the 6th); November 2026 starts on a Sunday (first Tuesday the 3rd,
first Monday the 2nd).  Counted on the calendar by hand.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text,ymd", [
    ("the first tuesday of the month", (2026, 11, 3)),
    ("the first day of the month", (2026, 11, 1)),
    ("the first week of the month", (2026, 11, 2)),
    ("the last day of the month", (2026, 10, 31)),
    ("the first tuesday of this month", (2026, 10, 6)),
    ("the first day of this month", (2026, 10, 1)),
])
def test_of_the_month(text, ymd):
    span, rest = extract_timespan(text, "en", SATURDAY)
    assert span.start == AstroDate(*ymd)
    assert rest == ""


@pytest.mark.parametrize("text,anchor,ymd", [
    # The first week of October 2026 is Monday 5 to Monday 12 (exclusive):
    # said at midnight on the 12th it has ended, so it is November's, which
    # starts on Monday 2 November.
    ("the first week of the month", datetime(2026, 10, 12), (2026, 11, 2)),
    # 1 October has ended at midnight on 2 October.
    ("the first day of the month", datetime(2026, 10, 2), (2026, 11, 1)),
    # Said at noon on 1 October, the first day of the month is still today.
    ("the first day of the month", datetime(2026, 10, 1, 12), (2026, 10, 1)),
])
def test_a_span_that_ends_at_the_anchor_has_passed(text, anchor, ymd):
    span, rest = extract_timespan(text, "en", anchor)
    assert span.start == AstroDate(*ymd)
    assert rest == ""


@pytest.mark.parametrize("text,anchor,ymd", [
    # A weekday said on that day is the anchor's day (a day is a span, and
    # the span that holds the anchor is the current one): the first Tuesday
    # of October 2026 is the 6th, so at noon on Tuesday 6 October it is
    # today.  On Wednesday the 7th it has passed, and November's first
    # Tuesday is the 3rd.  The last Friday of October 2026 is the 30th.
    ("the first tuesday of the month", datetime(2026, 10, 6, 12),
     (2026, 10, 6)),
    ("the first tuesday of the month", datetime(2026, 10, 7, 12),
     (2026, 11, 3)),
    ("the last friday of the month", datetime(2026, 10, 30, 12),
     (2026, 10, 30)),
])
def test_a_weekday_said_on_that_day_is_today(text, anchor, ymd):
    span, rest = extract_timespan(text, "en", anchor)
    assert span.start == AstroDate(*ymd)
    assert rest == ""


# A "since" endpoint and the left end of a range ending today name a past
# start: the latest such day at or before the anchor, never next month's.
# The bare phrase rolls (ruling 13); the endpoint steps back one month at a
# time and counts the day in its own month.  On Saturday 17 October 2026 the
# first Tuesday of October is the 6th and the first day the 1st.  On
# Thursday 10 December 2026 the first day of December is the 1st, and
# 1 December 2026 is a Tuesday, so it is also the first Tuesday.
SAT17 = datetime(2026, 10, 17, 12, 0)
THU10 = datetime(2026, 12, 10, 10, 0)


@pytest.mark.parametrize("lang,text,anchor,begin,end", [
    ("en", "since the first tuesday of the month", SAT17,
     (2026, 10, 6), (2026, 10, 17, 12)),
    ("en", "since the first day of the month", SAT17,
     (2026, 10, 1), (2026, 10, 17, 12)),
    ("pt", "desde a primeira terça-feira do mês", SAT17,
     (2026, 10, 6), (2026, 10, 17, 12)),
    ("pt", "desde o primeiro dia do mês", SAT17,
     (2026, 10, 1), (2026, 10, 17, 12)),
    ("es", "desde el primer martes del mes", SAT17,
     (2026, 10, 6), (2026, 10, 17, 12)),
    ("es", "desde el primer día del mes", SAT17,
     (2026, 10, 1), (2026, 10, 17, 12)),
    ("fr", "depuis le premier mardi du mois", SAT17,
     (2026, 10, 6), (2026, 10, 17, 12)),
    ("fr", "depuis le premier jour du mois", SAT17,
     (2026, 10, 1), (2026, 10, 17, 12)),
    ("de", "seit dem ersten Dienstag des Monats", SAT17,
     (2026, 10, 6), (2026, 10, 17, 12)),
    ("de", "seit dem ersten Tag des Monats", SAT17,
     (2026, 10, 1), (2026, 10, 17, 12)),
    ("en", "from the first day of the month to today", SAT17,
     (2026, 10, 1), (2026, 10, 18)),
    ("en", "from the first day of the month to today", THU10,
     (2026, 12, 1), (2026, 12, 11)),
    ("en", "from the first tuesday of the month to today", THU10,
     (2026, 12, 1), (2026, 12, 11)),
    ("pt", "do primeiro dia do mês até hoje", THU10,
     (2026, 12, 1), (2026, 12, 11)),
])
def test_a_past_anchored_endpoint_steps_back_by_months(lang, text, anchor,
                                                      begin, end):
    span, rest = extract_timespan(text, lang, anchor)
    assert (span.start, span.end) == (AstroDate(*begin), AstroDate(*end))
    assert rest == ""


# A right endpoint that recurs each month stays in its month and is never
# rolled by weeks.  October 2026 Tuesdays are the 6th, 13th, 20th and 27th;
# its Fridays are the 2nd, 9th, 16th, 23rd and 30th.  So on Saturday
# 17 October the left end steps back to October and the range ends after
# 20 October or after 30 October.
@pytest.mark.parametrize("lang,text,begin,end", [
    ("en", "from the first tuesday of the month to the third tuesday of the "
     "month", (2026, 10, 6), (2026, 10, 21)),
    ("en", "between the first tuesday of the month and the third tuesday of "
     "the month", (2026, 10, 6), (2026, 10, 21)),
    ("en", "from the first tuesday of the month to the last friday of the "
     "month", (2026, 10, 6), (2026, 10, 31)),
    ("en", "from the first day of the month to the last friday of the month",
     (2026, 10, 1), (2026, 10, 31)),
    ("pt", "desde a primeira terça-feira do mês até à terceira terça-feira "
     "do mês", (2026, 10, 6), (2026, 10, 21)),
    ("pt", "desde a primeira terça-feira do mês até à última sexta-feira do "
     "mês", (2026, 10, 6), (2026, 10, 31)),
    ("pt", "do primeiro dia do mês até à última sexta-feira do mês",
     (2026, 10, 1), (2026, 10, 31)),
    ("es", "del primer martes del mes al tercer martes del mes",
     (2026, 10, 6), (2026, 10, 21)),
    ("es", "del primer martes del mes al último viernes del mes",
     (2026, 10, 6), (2026, 10, 31)),
    ("es", "del primer día del mes al último viernes del mes",
     (2026, 10, 1), (2026, 10, 31)),
    ("fr", "du premier mardi du mois au troisième mardi du mois",
     (2026, 10, 6), (2026, 10, 21)),
    ("fr", "du premier mardi du mois au dernier vendredi du mois",
     (2026, 10, 6), (2026, 10, 31)),
    ("fr", "du premier jour du mois au dernier vendredi du mois",
     (2026, 10, 1), (2026, 10, 31)),
    ("de", "vom ersten Dienstag des Monats bis zum dritten Dienstag des "
     "Monats", (2026, 10, 6), (2026, 10, 21)),
    ("de", "vom ersten Dienstag des Monats bis zum letzten Freitag des "
     "Monats", (2026, 10, 6), (2026, 10, 31)),
    ("de", "vom ersten Tag des Monats bis zum letzten Freitag des Monats",
     (2026, 10, 1), (2026, 10, 31)),
    ("en", "from the 3rd of the month to the third tuesday of the month",
     (2026, 10, 3), (2026, 10, 21)),
    ("en", "from the 3rd of the month to the last friday of the month",
     (2026, 10, 3), (2026, 10, 31)),
])
def test_a_monthly_right_endpoint_is_not_rolled_by_weeks(lang, text, begin,
                                                         end):
    span, rest = extract_timespan(text, lang, SAT17)
    assert (span.start, span.end) == (AstroDate(*begin), AstroDate(*end))
    assert rest == ""


# The nth weekday of the month skips a month that lacks it (ruling 13).
# Saturday 31 October 2026: the Fridays of October are the 2nd, 9th, 16th,
# 23rd and 30th.  November 2026 starts on a Sunday and December on a
# Tuesday, so each has four Fridays; January 2027 starts on a Friday, so its
# fifth Friday is the 29th.  October has four Sundays (4, 11, 18, 25) and
# November five (1, 8, 15, 22, 29).
SAT31 = datetime(2026, 10, 31, 12, 0)


@pytest.mark.parametrize("text,ymd", [
    ("the fifth friday of the month", (2027, 1, 29)),
    ("the fifth sunday of the month", (2026, 11, 29)),
])
def test_an_nth_weekday_skips_a_month_that_lacks_it(text, ymd):
    span, rest = extract_timespan(text, "en", SAT31)
    assert span.start == AstroDate(*ymd)
    assert rest == ""


# "since" and the left end of a range step back to the latest such weekday:
# the fifth Friday of October is the 30th.  September 2026 starts on a
# Tuesday and has four Sundays; August 2026 starts on a Saturday, so its
# fifth Sunday is the 30th.
@pytest.mark.parametrize("lang,text,begin,end", [
    ("en", "since the fifth friday of the month", (2026, 10, 30),
     (2026, 10, 31, 12)),
    ("pt", "desde a quinta sexta-feira do mês", (2026, 10, 30),
     (2026, 10, 31, 12)),
    ("es", "desde el quinto viernes del mes", (2026, 10, 30),
     (2026, 10, 31, 12)),
    ("fr", "depuis le cinquième vendredi du mois", (2026, 10, 30),
     (2026, 10, 31, 12)),
    ("de", "seit dem fünften Freitag des Monats", (2026, 10, 30),
     (2026, 10, 31, 12)),
    ("en", "from the fifth friday of the month to today", (2026, 10, 30),
     (2026, 11, 1)),
    ("en", "since the fifth sunday of the month", (2026, 8, 30),
     (2026, 10, 31, 12)),
])
def test_a_past_fifth_weekday_steps_back_to_a_month_that_has_it(lang, text,
                                                               begin, end):
    span, rest = extract_timespan(text, lang, SAT31)
    assert (span.start, span.end) == (AstroDate(*begin), AstroDate(*end))
    assert rest == ""


# "since the last friday of the month" and "from the last friday of the month
# to today" name the same start.  On 17 October the last Friday of October
# (the 30th) is ahead, so both step back to the last Friday of September:
# September 2026 starts on a Tuesday, so its Fridays are 4, 11, 18 and 25.
# On 31 October the last Friday of October, the 30th, has passed.
@pytest.mark.parametrize("text,anchor,begin,end", [
    ("since the last friday of the month", SAT17, (2026, 9, 25),
     (2026, 10, 17, 12)),
    ("from the last friday of the month to today", SAT17, (2026, 9, 25),
     (2026, 10, 18)),
    ("since the last friday of the month", SAT31, (2026, 10, 30),
     (2026, 10, 31, 12)),
    ("from the last friday of the month to today", SAT31, (2026, 10, 30),
     (2026, 11, 1)),
])
def test_since_and_range_agree_on_the_last_weekday(text, anchor, begin, end):
    span, rest = extract_timespan(text, "en", anchor)
    assert (span.start, span.end) == (AstroDate(*begin), AstroDate(*end))
    assert rest == ""


def test_since_the_last_weekday_of_this_month_ahead_names_no_start():
    got = extract_timespan("since the last friday of this month", "en", SAT17)
    assert got is None or got[1] != ""


# A right end that recurs each month and still lies before the left end names
# no range, and the left end is not pulled back a year.  December 2026
# Thursdays are 3, 10, 17, 24 and 31; the Sunday after Monday 28 December is
# 3 January 2027, and tomorrow on Thursday 31 December is 1 January 2027.
MON28 = datetime(2026, 12, 28, 12, 0)
THU31 = datetime(2026, 12, 31, 12, 0)


@pytest.mark.parametrize("lang,text,anchor", [
    ("en", "from sunday to the last thursday of the month", MON28),
    ("en", "between sunday and the last thursday of the month", MON28),
    ("en", "from january 2 to the last thursday of the month", MON28),
    ("en", "from sunday to the fifth thursday of the month", MON28),
    ("en", "from tomorrow to the last thursday of the month", THU31),
    ("en", "from sunday to the 31st of the month", MON28),
    ("en", "from tomorrow to the 31st of the month", THU31),
    ("pt", "de domingo até à última quinta-feira do mês", MON28),
    ("pt", "de amanhã até à última quinta-feira do mês", THU31),
    ("es", "del domingo al último jueves del mes", MON28),
    ("fr", "de dimanche au dernier jeudi du mois", MON28),
    ("de", "von Sonntag bis zum letzten Donnerstag des Monats", MON28),
])
def test_a_monthly_right_end_before_the_left_end_names_no_range(lang, text,
                                                                anchor):
    got = extract_timespan(text, lang, anchor)
    assert got is None or got[1] != "", f"read {got!r}"


# "since X until today" ends today, whatever X is: a day word counts from
# now, not from the start.  On Saturday 17 October 2026 the Monday before is
# the 12th; on Tuesday 10 November the fifth Friday of October is the 30th.
@pytest.mark.parametrize("text,anchor,begin,end", [
    ("since the last friday of the month until tomorrow", SAT17,
     (2026, 9, 25), (2026, 10, 19)),
    ("since the last friday of the month until today", SAT17,
     (2026, 9, 25), (2026, 10, 18)),
    ("since the fifth friday of the month until today",
     datetime(2026, 11, 10, 12, 0), (2026, 10, 30), (2026, 11, 11)),
    ("since the first tuesday of the month until today", SAT17,
     (2026, 10, 6), (2026, 10, 18)),
    ("since monday until today", SAT17, (2026, 10, 12), (2026, 10, 18)),
    ("since monday until yesterday", SAT17, (2026, 10, 12), (2026, 10, 17)),
    ("since yesterday until tomorrow", SAT17, (2026, 10, 16), (2026, 10, 19)),
    ("since monday until friday", SAT17, (2026, 10, 12), (2026, 10, 17)),
])
def test_since_until_a_day_word_counts_from_now(text, anchor, begin, end):
    span, rest = extract_timespan(text, "en", anchor)
    assert (span.start, span.end) == (AstroDate(*begin), AstroDate(*end))
    assert rest == ""
