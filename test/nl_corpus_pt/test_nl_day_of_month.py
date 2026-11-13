# -*- coding: utf-8 -*-
"""A numbered day of the month without a month name, pt.

"dia N" names a numbered day of the month (Priberam s.v. "dia", "dia de
Reis": "Dia 6 de Janeiro ...").  Without a month name the next day with that
number is meant, and the anchor's own day when it has that number.  A month
that lacks the day is skipped.  "o próximo dia N" is "Seguinte ao actual"
(Priberam s.v. "próximo", 4): the next such day strictly after today.

Anchor Tuesday 2017-06-27 13:04.  The 5th and the 3rd have passed in June,
so they are 5 and 3 July; the 30th and the 28th are still ahead in June.
Anchor Saturday 2026-01-31: February 2026 has no 29th or 30th, so those are
29 and 30 March; the 28th is 28 February.  Counted on the calendar by hand.
"""
from datetime import datetime

import pytest

from ._corpus import ANCHOR, ad, nomatch, parse

JAN31 = datetime(2026, 1, 31, 12, 0)


@pytest.mark.parametrize("text,expected,rest", [
    ("o dia 5 do mês", datetime(2017, 7, 5), ""),
    ("o dia 30 do mês", datetime(2017, 6, 30), ""),
    ("no dia 3", datetime(2017, 7, 3), ""),
    ("dia 28", datetime(2017, 6, 28), ""),
    ("no dia 27", datetime(2017, 6, 27), ""),
    ("no dia 3 às 10h", datetime(2017, 7, 3, 10), ""),
    ("o próximo dia 5", datetime(2017, 7, 5), ""),
    ("o próximo dia 27", datetime(2017, 7, 27), ""),
    ("o dia 25 de dezembro", datetime(2017, 12, 25), ""),
    ("no dia 3 de julho", datetime(2017, 7, 3), ""),
    ("a reunião é no dia 3", datetime(2017, 7, 3), "a reunião é"),
])
def test_day_of_month(text, expected, rest):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(expected)
    assert r.remainder == rest


@pytest.mark.parametrize("text,expected", [
    ("o dia 30 do mês", datetime(2026, 3, 30)),
    ("o dia 29 do mês", datetime(2026, 3, 29)),
    ("o dia 28 do mês", datetime(2026, 2, 28)),
])
def test_day_of_month_skips_a_month_without_the_day(text, expected):
    r = parse(text, JAN31)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(expected)


@pytest.mark.parametrize("text", [
    "o dia foi longo",
    "o dia 40",
    "o último dia 5",
])
def test_not_a_day_of_month(text):
    nomatch(text)


# "desde o dia N" opens a span at the most recent day N at or before now.  A
# numbered day recurs each month, so the start steps back one month at a
# time, and a month that lacks the day is skipped.  A clock stays with its
# day.  Anchor Tuesday 2017-06-27 13:04: the 3rd, 1st, 20th, 5th and 15th
# have passed in June; the 30th has not, and May has 31 days, so the 30th is
# 30 May; the 27th is today; today's 15:00 is still ahead, so "o dia 27 às
# 15h" is 27 May.  Saturday 2017-07-01: June has no 31st, so the 31st is
# 31 May.  Wednesday 2017-03-01: February 2017 has no 29th, so the 29th is
# 29 January.  Counted on the calendar by hand.
JUL01 = datetime(2017, 7, 1, 12, 0)
MAR01 = datetime(2017, 3, 1, 12, 0)


@pytest.mark.parametrize("text,anchor,expected", [
    ("desde o dia 3", ANCHOR, datetime(2017, 6, 3)),
    ("desde o dia 1", ANCHOR, datetime(2017, 6, 1)),
    ("desde o dia 30", ANCHOR, datetime(2017, 5, 30)),
    ("desde dia 20", ANCHOR, datetime(2017, 6, 20)),
    ("desde o dia 27", ANCHOR, datetime(2017, 6, 27)),
    ("desde o dia 5 do mês", ANCHOR, datetime(2017, 6, 5)),
    ("desde o dia 15 às 10h", ANCHOR, datetime(2017, 6, 15, 10)),
    ("desde o dia 27 às 15h", ANCHOR, datetime(2017, 5, 27, 15)),
    ("desde o dia 31", JUL01, datetime(2017, 5, 31)),
    ("desde o dia 29", MAR01, datetime(2017, 1, 29)),
])
def test_since_day_of_month_steps_back_by_months(text, anchor, expected):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(expected), ad(anchor))
    assert r.remainder == ""


# The yearly and daily cycles stay: a named date rolls back by years, a bare
# clock by days.
@pytest.mark.parametrize("text,expected", [
    ("desde 5 de março", datetime(2017, 3, 5)),
    ("desde 30 de dezembro", datetime(2016, 12, 30)),
    ("desde o dia 30 de dezembro", datetime(2016, 12, 30)),
    ("desde as 15h", datetime(2017, 6, 26, 15)),
])
def test_since_other_cycles_unchanged(text, expected):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(expected)


# The left end of a range ending today or yesterday is the latest day N at
# or before the right end, a month or more back, never a year back.  Sunday
# 2017-12-10: the 3rd and the 1st have passed in December, so "do dia 3 até
# hoje" runs from 3 December to the end of the 10th.  Sunday 2017-12-31
# 23:59: yesterday is the 30th, and the 20th has passed.  Tuesday
# 2017-06-27: the 3rd has passed in June.  Counted on the calendar by hand.
DEC10 = datetime(2017, 12, 10, 10, 0)
DEC31 = datetime(2017, 12, 31, 23, 59)


@pytest.mark.parametrize("text,anchor,begin,end", [
    ("do dia 3 até hoje", DEC10, datetime(2017, 12, 3), datetime(2017, 12, 11)),
    ("entre o dia 1 e hoje", DEC10, datetime(2017, 12, 1),
     datetime(2017, 12, 11)),
    ("desde o dia 3 até ontem", DEC10, datetime(2017, 12, 3),
     datetime(2017, 12, 10)),
    ("do dia 20 até ontem", DEC31, datetime(2017, 12, 20),
     datetime(2017, 12, 31)),
    ("do dia 3 até hoje", ANCHOR, datetime(2017, 6, 3), datetime(2017, 6, 28)),
])
def test_range_from_day_of_month_steps_back_by_months(text, anchor, begin,
                                                       end):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(begin), ad(end))
    assert r.remainder == ""


# A weekday said beside "dia N" must fall on that day.  20 June 2017 is a
# Tuesday, so "desde terça dia 20" said on Tuesday 27 June starts on the
# 20th.  It is not a Wednesday, so "desde quarta dia 20" names no start.
def test_since_weekday_with_day_of_month_agrees():
    r = parse("desde terça dia 20")
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2017, 6, 20)),
                                          ad(ANCHOR))
    assert r.remainder in ("", "terça")


def test_since_weekday_that_disagrees_with_the_day_names_no_start():
    r = parse("desde quarta dia 20")
    assert r is None or r.remainder != "", f"read {r!r}"
    assert r is None or r.span.start != ad(datetime(2017, 6, 20))


# A weekday beside "dia N" that is not that day's weekday names no range: the
# left end is not pulled back a year in its place.  Wednesday 2017-12-27:
# 20 December 2017 is a Wednesday, not a Tuesday.  On Tuesday 2017-06-27,
# 20 June 2017 is a Tuesday, so the range starts on the 20th.
DEC27 = datetime(2017, 12, 27, 10, 0)


@pytest.mark.parametrize("text", [
    "do dia 20, terça, até hoje",
    "entre o dia 20, terça, e hoje",
    "do dia 20, terça, até ontem",
    "de terça dia 20 até hoje",
])
def test_range_weekday_that_disagrees_with_the_day_names_no_range(text):
    r = parse(text, DEC27)
    assert r is None or r.remainder != "", f"read {r!r}"
    assert r is None or r.span.start.year == 2018, f"read {r!r}"


@pytest.mark.parametrize("text,anchor,begin,end", [
    ("do dia 20, quarta, até hoje", DEC27, datetime(2017, 12, 20),
     datetime(2017, 12, 28)),
    ("do dia 20, terça, até hoje", ANCHOR, datetime(2017, 6, 20),
     datetime(2017, 6, 28)),
])
def test_range_weekday_that_agrees_with_the_day(text, anchor, begin, end):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(begin), ad(end))
    assert r.remainder == ""


# A weekday after "o dia N" names that day or no day (ruling 15).  On
# Tuesday 2017-06-27 the next 20th is 20 July 2017, a Thursday.
@pytest.mark.parametrize("text", [
    "o dia 20, quarta",
    "o dia 20, terça",
    "no dia 20, sábado",
])
def test_weekday_after_the_day_that_disagrees_is_not_folded(text):
    r = parse(text)
    assert r is None or r.remainder != "", f"read {r!r}"


@pytest.mark.parametrize("text", ["o dia 20, quinta", "no dia 20, quinta-feira"])
def test_weekday_after_the_day_that_agrees_is_folded(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(datetime(2017, 7, 20))
    assert r.remainder == ""


def test_since_day_with_weekday_after_it_that_agrees():
    r = parse("desde o dia 20, terça")
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2017, 6, 20)),
                                          ad(ANCHOR))
    assert r.remainder == ""


# A right end that recurs each month is not rolled by weeks.  Saturday
# 2026-10-17: the 3rd has passed in October; October 2026 Tuesdays are 6,
# 13, 20 and 27, and its last Friday is the 30th.
SAT17 = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text,begin,end", [
    ("do dia 3 até à terceira terça-feira do mês", datetime(2026, 10, 3),
     datetime(2026, 10, 21)),
    ("do dia 3 até à última sexta-feira do mês", datetime(2026, 10, 3),
     datetime(2026, 10, 31)),
])
def test_range_to_a_monthly_weekday_is_not_rolled_by_weeks(text, begin, end):
    r = parse(text, SAT17)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(begin), ad(end))
    assert r.remainder == ""


# A numbered day of the month that lies before the left end names no range,
# and the left end is not pulled back a year.  The Sunday after Monday
# 2026-12-28 is 3 January 2027; tomorrow on Thursday 2026-12-31 is 1 January.
@pytest.mark.parametrize("text,anchor", [
    ("de domingo até ao dia 31", datetime(2026, 12, 28, 12, 0)),
    ("de domingo até ao dia 30", datetime(2026, 12, 28, 12, 0)),
    ("de amanhã até ao dia 31", datetime(2026, 12, 31, 12, 0)),
])
def test_range_to_a_day_of_month_before_the_left_end_names_no_range(text,
                                                                     anchor):
    r = parse(text, anchor)
    assert r is None or r.remainder != "", f"read {r!r}"
