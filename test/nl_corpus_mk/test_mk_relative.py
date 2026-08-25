"""Relative time: the count-form plurals, and last/next said per unit.

A noun behind a numeral takes its count form, a different word from its general
plural -- дена counts days and денови does not, часа counts hours and часови
does not -- so both halves of that split are asserted, the count form reading
and the general form refusing.

Last and next are not one construction here.  The year has its own two adverbs,
лани and догодина, each a single word.  Every other unit and every weekday takes
минат or следен, and the adjective agrees in gender with the noun it selects:
минатиот месец is masculine, минатата седмица feminine, минатото тримесечје
neuter.  The agreeing form is the one that ships, so the wrong-gender spelling
is not a second way to say the same thing.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, day, nomatch, parse, span, start, start_end


def ago(**kw):
    return ad(ANCHOR - timedelta(**kw))


def ahead(**kw):
    return ad(ANCHOR + timedelta(**kw))


# -- count form vs general plural -------------------------------------------

@pytest.mark.parametrize("text,kw", [
    ("пред 2 дена", {"days": 2}),
    ("пред 5 дена", {"days": 5}),
    ("пред 3 часа", {"hours": 3}),
    ("пред 12 часа", {"hours": 12}),
    ("пред 10 минути", {"minutes": 10}),
    ("пред 30 секунди", {"seconds": 30}),
])
def test_the_count_form_counts(text, kw):
    assert start(text) == ago(**kw)


@pytest.mark.parametrize("text", [
    "пред 5 денови", "пред 2 денови", "пред 3 часови", "пред 12 часови",
])
def test_the_general_plural_does_not_count(text):
    nomatch(text)


@pytest.mark.parametrize("text,kw", [
    ("за 2 дена", {"days": 2}),
    ("за 3 часа", {"hours": 3}),
    ("за 45 минути", {"minutes": 45}),
    ("за 10 секунди", {"seconds": 10}),
])
def test_the_forward_marker_takes_the_same_forms(text, kw):
    assert start(text) == ahead(**kw)


@pytest.mark.parametrize("text,weeks", [
    ("пред 2 седмици", 2), ("пред 3 седмици", 3), ("пред 2 недели", 2),
])
def test_weeks_counted(text, weeks):
    assert start(text) == ago(weeks=weeks)


@pytest.mark.parametrize("text", ["пред 3 месеци", "пред 3 месеца"])
def test_months_counted(text):
    # Three months back from the twelfth of May is the twelfth of February;
    # месеци is the plural CLDR counts months with and месеца the count form
    # the dictionary gives, and both are current.
    assert (start(text).year, start(text).month) == (2027, 2)


@pytest.mark.parametrize("text,years", [("пред 2 години", 2),
                                        ("пред 11 години", 11)])
def test_years_counted_back(text, years):
    assert start(text).year == ANCHOR.year - years


@pytest.mark.parametrize("text,years", [("за 4 години", 4),
                                        ("за 10 години", 10)])
def test_years_counted_forward(text, years):
    assert start(text).year == ANCHOR.year + years


# -- the year's own two words -----------------------------------------------

def test_last_year_is_one_word():
    assert start_end("лани") == (ad(ANCHOR.replace(year=2026, month=1, day=1,
                                                   hour=0, minute=0)),
                                 ad(ANCHOR.replace(year=2027, month=1, day=1,
                                                   hour=0, minute=0)))


def test_next_year_is_one_word():
    assert start_end("догодина") == (
        ad(ANCHOR.replace(year=2028, month=1, day=1, hour=0, minute=0)),
        ad(ANCHOR.replace(year=2029, month=1, day=1, hour=0, minute=0)))


def test_the_periphrastic_year_reads_the_same_as_the_adverb():
    assert start_end("минатата година") == start_end("лани")
    assert start_end("следната година") == start_end("догодина")


def test_this_year_has_no_dedicated_word():
    assert start_end("оваа година") == (
        ad(ANCHOR.replace(year=2027, month=1, day=1, hour=0, minute=0)),
        ad(ANCHOR.replace(year=2028, month=1, day=1, hour=0, minute=0)))


# -- last/next with gender agreement ----------------------------------------

@pytest.mark.parametrize("text,y,m", [
    ("минатиот месец", 2027, 4),
    ("овој месец", 2027, 5),
    ("следниот месец", 2027, 6),
])
def test_the_month_takes_the_masculine(text, y, m):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (y, m, 1)


@pytest.mark.parametrize("text,first", [
    ("минатата седмица", (2027, 5, 3)),
    ("оваа седмица", (2027, 5, 10)),
    ("следната седмица", (2027, 5, 17)),
])
def test_the_week_takes_the_feminine(text, first):
    assert start_end(text) == (day(*first)[0],
                               day(first[0], first[1], first[2] + 7)[0])


@pytest.mark.parametrize("text,q_start,q_end", [
    ("минатото тримесечје", (2027, 1, 1), (2027, 4, 1)),
    ("ова тримесечје", (2027, 4, 1), (2027, 7, 1)),
    ("следното тримесечје", (2027, 7, 1), (2027, 10, 1)),
])
def test_the_quarter_takes_the_neuter(text, q_start, q_end):
    assert start_end(text) == (day(*q_start)[0], day(*q_end)[0])


@pytest.mark.parametrize("text,date_", [
    ("минатиот понеделник", (2027, 5, 10)),
    ("овој понеделник", (2027, 5, 10)),
    ("следниот понеделник", (2027, 5, 17)),
    ("минатиот петок", (2027, 5, 7)),
    ("следниот петок", (2027, 5, 14)),
    ("минатата среда", (2027, 5, 5)),
    ("следната среда", (2027, 5, 19)),
    ("минатата сабота", (2027, 5, 8)),
    ("следната сабота", (2027, 5, 15)),
    ("минатиот вторник", (2027, 5, 11)),
    ("следниот четврток", (2027, 5, 13)),
])
def test_a_weekday_agrees_with_its_own_gender(text, date_):
    # минат selects the last occurrence strictly before the Wednesday anchor,
    # следен the next one strictly after it.
    assert start_end(text) == day(*date_)


def test_the_weekday_and_the_week_are_different_nouns():
    # недела on its own is Sunday; the week is седмица, which is the noun CLDR
    # names the week field with.  So the two phrases below are a day apart in
    # length, not two spellings of one span.
    assert start_end("следната недела") == day(2027, 5, 16)
    assert start_end("следната седмица") == (day(2027, 5, 17)[0],
                                             day(2027, 5, 24)[0])


# -- named days --------------------------------------------------------------

@pytest.mark.parametrize("text,date_", [
    ("завчера", (2027, 5, 10)),
    ("вчера", (2027, 5, 11)),
    ("денес", (2027, 5, 12)),
    ("денеска", (2027, 5, 12)),
    ("утре", (2027, 5, 13)),
    ("задутре", (2027, 5, 14)),
    ("другиден", (2027, 5, 14)),
])
def test_the_five_named_days(text, date_):
    assert start_end(text) == day(*date_)
