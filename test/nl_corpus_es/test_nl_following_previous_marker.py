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

_MARKERS = ('siguiente', 'anterior',)


@pytest.mark.parametrize("text,begin,end", [
    ('el viernes siguiente', datetime(2017, 6, 30), datetime(2017, 7, 1)),
    ('la semana siguiente', datetime(2017, 7, 3), datetime(2017, 7, 10)),
    ('el mes anterior', datetime(2017, 5, 1), datetime(2017, 6, 1)),
    ('el año siguiente', datetime(2018, 1, 1), datetime(2019, 1, 1)),
    ('el año anterior', datetime(2016, 1, 1), datetime(2017, 1, 1)),
])
def test_marker_gives_the_period(text, begin, end):
    assert start_end(text) == (ad(begin), ad(end))


@pytest.mark.parametrize("text", [
    'el viernes siguiente',
    'la semana siguiente',
    'el mes anterior',
    'el año siguiente',
    'el año anterior',
])
def test_marker_is_consumed(text):
    remainder = parse(text)[1]
    assert not any(w in remainder.split() for w in _MARKERS), remainder


@pytest.mark.parametrize("text", [
    'el siguiente paso',
    'la página anterior',
])
def test_marker_in_a_non_date_sense_gives_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    'las semanas siguientes',
    'los meses anteriores',
    'en las semanas siguientes cerramos el trato',
    'los días anteriores a la boda',
])
def test_plural_marker_with_a_plural_unit_names_no_single_period(text):
    nomatch(text)
