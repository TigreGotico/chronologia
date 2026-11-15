# -*- coding: utf-8 -*-
"""A postposed or prefixed "following"/"previous" marker is read, not left in
the remainder, and the same words in a non-date sense name no date.

The anchor is Tuesday 2017-06-27 13:04.  A weekday gives the coming day; a
period gives the whole calendar unit.  Gold values are hand arithmetic from
the anchor: the next week starts Monday 2017-07-03, the next month on
2017-07-01, the next year on 2018-01-01, the previous month on 2017-05-01 and
the previous year on 2016-01-01.
"""
from datetime import datetime

import pytest

from ._corpus import ad, nomatch, parse, start_end

_MARKERS = ('following',)


@pytest.mark.parametrize("text,begin,end", [
    ('the following friday', datetime(2017, 6, 30), datetime(2017, 7, 1)),
    ('the following week', datetime(2017, 7, 3), datetime(2017, 7, 10)),
    ('the following year', datetime(2018, 1, 1), datetime(2019, 1, 1)),
    ('the following month', datetime(2017, 7, 1), datetime(2017, 8, 1)),
])
def test_marker_gives_the_period(text, begin, end):
    assert start_end(text) == (ad(begin), ad(end))


@pytest.mark.parametrize("text", [
    'the following friday',
    'the following week',
    'the following year',
    'the following month',
])
def test_marker_is_consumed(text):
    remainder = parse(text)[1]
    assert not any(w in remainder.split() for w in _MARKERS), remainder


@pytest.mark.parametrize("text", [
    'the following items',
])
def test_marker_in_a_non_date_sense_gives_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "following weeks of delays the project shipped",
    "following weeks of delays, the project shipped",
    "following months of talks, a deal",
    "following years of research they found it",
    "following days of rain the river rose",
])
def test_bare_following_as_a_preposition_gives_none(text):
    nomatch(text)


def test_the_following_week_leaves_nothing_in_the_remainder():
    assert parse("the following week")[1] == ""


@pytest.mark.parametrize("text", [
    "the following months",
    "the following days",
    "the following weeks were hard",
    "in the following weeks we will ship",
    "the following years were good",
    "the following quarters were weak",
    "the following weekends",
    "the following weekends were busy",
])
def test_the_following_with_a_plural_unit_names_no_single_period(text):
    nomatch(text)


@pytest.mark.parametrize("text,begin,end", [
    ("the following 3 weeks", datetime(2017, 6, 27), datetime(2017, 7, 18)),
    ("the following weekend", datetime(2017, 7, 8), datetime(2017, 7, 10)),
    ("the following quarter", datetime(2017, 7, 1), datetime(2017, 10, 1)),
    ("the following monday", datetime(2017, 7, 3), datetime(2017, 7, 4)),
])
def test_the_following_with_a_singular_period_survives(text, begin, end):
    assert start_end(text) == (ad(begin), ad(end))
