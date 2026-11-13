# -*- coding: utf-8 -*-
"""A count with a weekday names that weekday in the period the count reaches, pt.

"daqui a uma semana sexta-feira" is the Friday of the calendar week one week
on, and the week starts on the locale's first day: Monday in pt-PT and Sunday
in pt-BR (CLDR ``weekData/firstDay``).  "daqui a um mês sexta-feira" and
"daqui a um ano sexta-feira" are the first Friday on or after the day the
count reaches.  A count of days reaches one day, so the weekday must be that
day's weekday, as with "amanhã, domingo": an "aposto" is a "Nome ou locução
nominal que se junta a outro nome para melhor o caracterizar" (Priberam s.v.
"aposto", 5).  When it is not, the phrase names no day and is refused.  The
weekday belongs to the date, so it never stays in the remainder.

Two cases do not fold.  A weekday before a count of days stands apart from
it, as "sexta-feira amanhã" does, so the weekday keeps its own reading and
the count stays in the remainder.  A weekday that labels a literal date
("sexta-feira 30 de outubro") belongs to that date, so the count stays in
the remainder.  Only an article or "on" links the two parts; a clause word
("que") does not.

Anchor Saturday 2026-10-17 12:00.  pt-PT weeks run Monday 12 to Sunday 18
October, then 19 to 25, then 26 October to 1 November; the week before runs
5 to 11.  pt-BR weeks run Sunday 11 to Saturday 17, then 18 to 24, then 25
to 31; the week before runs 4 to 10.  17 November 2026 is a Tuesday and 17
October 2027 a Sunday.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ad

SATURDAY = datetime(2026, 10, 17, 12, 0)


def day(m, d, y=2026, h=0):
    return ad(datetime(y, m, d, h))


@pytest.mark.parametrize("lang,text,expected", [
    ("pt-PT", "daqui a uma semana sexta-feira", day(10, 23)),
    ("pt-BR", "daqui a uma semana sexta-feira", day(10, 23)),
    ("pt-PT", "daqui a uma semana segunda-feira", day(10, 19)),
    ("pt-BR", "daqui a uma semana segunda-feira", day(10, 19)),
    ("pt-PT", "daqui a uma semana domingo", day(10, 25)),
    ("pt-BR", "daqui a uma semana domingo", day(10, 18)),
    ("pt-PT", "dentro de duas semanas sexta-feira", day(10, 30)),
    ("pt-BR", "dentro de duas semanas domingo", day(10, 25)),
    ("pt-PT", "em duas semanas sexta-feira", day(10, 30)),
    ("pt-BR", "em 2 semanas na sexta", day(10, 30)),
    ("pt-PT", "daqui a uma semana, na sexta-feira", day(10, 23)),
    ("pt-PT", "há uma semana sexta-feira", day(10, 9)),
    ("pt-BR", "há uma semana domingo", day(10, 4)),
    ("pt-PT", "há duas semanas domingo", day(10, 4)),
    ("pt-PT", "sexta-feira daqui a uma semana", day(10, 23)),
    ("pt-PT", "domingo daqui a uma semana", day(10, 25)),
    ("pt-BR", "domingo daqui a uma semana", day(10, 18)),
])
def test_a_weekday_after_a_count_of_weeks(lang, text, expected):
    r = extract_timespan(text, lang, SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (expected, expected + timedelta(days=1))
    assert r.remainder == ""


@pytest.mark.parametrize("lang,text,expected", [
    ("pt-PT", "daqui a um mês sexta-feira", day(11, 20)),
    ("pt-BR", "daqui a um mês terça-feira", day(11, 17)),
    ("pt-PT", "dentro de um mês segunda-feira", day(11, 23)),
    ("pt-PT", "daqui a um ano sexta-feira", day(10, 22, 2027)),
    ("pt-BR", "daqui a um ano domingo", day(10, 17, 2027)),
    ("pt-PT", "sexta-feira daqui a um mês", day(11, 20)),
])
def test_a_weekday_after_a_count_of_months_or_years(lang, text, expected):
    r = extract_timespan(text, lang, SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (expected, expected + timedelta(days=1))
    assert r.remainder == ""


def test_a_month_count_clamped_to_february():
    # 31 January 2026 plus a month is 28 February, a Saturday; the first
    # Friday on or after it is 6 March.
    r = extract_timespan("daqui a um mês sexta-feira", "pt-PT",
                         datetime(2026, 1, 31, 12, 0))
    assert r.span.start == day(3, 6)
    assert r.remainder == ""


@pytest.mark.parametrize("lang,text,expected", [
    ("pt-PT", "daqui a uma semana sexta-feira às 10h", day(10, 23, h=10)),
    ("pt-BR", "daqui a um mês sexta-feira às 15h", day(11, 20, h=15)),
])
def test_the_folded_weekday_takes_a_clock(lang, text, expected):
    r = extract_timespan(text, lang, SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == expected
    assert r.remainder == ""


def test_a_count_of_days_with_its_own_weekday():
    # Saturday plus two days is Monday 19.
    r = extract_timespan("daqui a dois dias segunda-feira", "pt-PT",
                         SATURDAY)
    assert r.span.start == day(10, 19)
    assert r.remainder == ""


@pytest.mark.parametrize("text", [
    "daqui a dois dias sexta-feira",
    "daqui a três dias domingo",
])
def test_a_count_of_days_with_another_weekday_is_refused(text):
    assert extract_timespan(text, "pt-PT", SATURDAY) is None


@pytest.mark.parametrize("text,expected,rest", [
    ("daqui a uma semana. sexta-feira trabalho", day(10, 24, h=12),
     "sexta-feira trabalho"),
    ("daqui a uma semana e sexta-feira", day(10, 24, h=12), "e sexta-feira"),
    ("há um mês sexta-feira", day(9, 17, h=12), "sexta-feira"),
    ("daqui a uma semana na próxima sexta-feira", day(10, 24, h=12),
     "na próxima sexta-feira"),
])
def test_no_fold_keeps_the_count(text, expected, rest):
    # No ruling names a weekday after a past month or a weekday with its own
    # marker, and a sentence end or a list joins two references, so the
    # count keeps its own reading: the anchor plus or minus the count, at
    # the anchor's clock (class 1).
    r = extract_timespan(text, "pt-PT", SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == expected
    assert r.remainder == rest


@pytest.mark.parametrize("text", [
    "daqui a uma semana, sexta-feira 30 de outubro",
    "daqui a uma semana sexta-feira 30 de outubro",
])
def test_a_weekday_that_labels_a_date_keeps_the_count(text):
    # Friday 30 October is the written date; the count does not move it.
    r = extract_timespan(text, "pt-PT", SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (day(10, 30), day(10, 31))
    assert r.remainder == "daqui a uma semana"


@pytest.mark.parametrize("text,expected,rest", [
    # The coming Friday is 23 October and the coming Monday 19 October.
    ("sexta-feira daqui a um dia", day(10, 23), "daqui a um dia"),
    ("sexta-feira daqui a dois dias", day(10, 23), "daqui a dois dias"),
    ("segunda-feira daqui a dois dias", day(10, 19), "daqui a dois dias"),
])
def test_a_weekday_before_a_count_of_days_keeps_the_count(text, expected,
                                                          rest):
    r = extract_timespan(text, "pt-PT", SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (expected,
                                          expected + timedelta(days=1))
    assert r.remainder == rest


def test_a_clause_word_does_not_link_a_count_to_a_weekday():
    # Saturday plus two days is Monday 19, at the anchor's clock.
    r = extract_timespan("daqui a dois dias que sexta-feira", "pt-PT",
                         SATURDAY)
    assert r is not None
    assert r.span.start == day(10, 19, h=12)
    assert r.remainder == "que sexta-feira"
