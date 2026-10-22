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

_MARKERS = ('seguinte', 'anterior',)


@pytest.mark.parametrize("text,begin,end", [
    ('o venres seguinte', datetime(2017, 6, 30), datetime(2017, 7, 1)),
    ('o ano seguinte', datetime(2018, 1, 1), datetime(2019, 1, 1)),
    ('o mes seguinte', datetime(2017, 7, 1), datetime(2017, 8, 1)),
    ('o mes anterior', datetime(2017, 5, 1), datetime(2017, 6, 1)),
])
def test_marker_gives_the_period(text, begin, end):
    assert start_end(text) == (ad(begin), ad(end))


@pytest.mark.parametrize("text", [
    'o venres seguinte',
    'o ano seguinte',
    'o mes seguinte',
    'o mes anterior',
])
def test_marker_is_consumed(text):
    remainder = parse(text)[1]
    assert not any(w in remainder.split() for w in _MARKERS), remainder


@pytest.mark.parametrize("text", [
    'o seguinte paso',
    'a páxina anterior',
])
def test_marker_in_a_non_date_sense_gives_none(text):
    nomatch(text)
