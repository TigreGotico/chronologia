"""nn: relative offsets both directions, named days, weekday refs."""
from datetime import timedelta

import pytest

from ._corpus import (ANCHOR, ad, start, start_end, span, nomatch, past,
                      future, AstroDate)


@pytest.mark.parametrize("text,n,unit", [('for tre dagar sidan', 3, 'day'), ('for ein dag sidan', 1, 'day'), ('for to veker sidan', 2, 'week'), ('for fem månader sidan', 5, 'month'), ('for eit år sidan', 1, 'year'), ('for ti år sidan', 10, 'year'), ('for ein time sidan', 1, 'hour'), ('for 30 minutt sidan', 30, 'minute'), ('for sju dagar sidan', 7, 'day')])
def test_past(text, n, unit):
    assert start_end(text) == past(n, unit)


@pytest.mark.parametrize("text,n,unit", [('om tre dagar', 3, 'day'), ('om to veker', 2, 'week'), ('om ein månad', 1, 'month'), ('om ti år', 10, 'year'), ('om ein time', 1, 'hour'), ('om 30 minutt', 30, 'minute'), ('om fire dagar', 4, 'day'), ('om eit år', 1, 'year')])
def test_future(text, n, unit):
    assert start_end(text) == future(n, unit)


@pytest.mark.parametrize("text,off", [('idag', 0), ('igår', -1), ('imorgon', 1), ('forgårs', -2), ('overmorgon', 2)])
def test_named_day(text, off):
    day = (ANCHOR + timedelta(days=off)).replace(hour=0, minute=0)
    assert start(text) == ad(day)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,date", [('neste måndag', (2017, 7, 3)), ('førre fredag', (2017, 6, 23)), ('neste tysdag', (2017, 7, 4)), ('førre måndag', (2017, 6, 26)), ('neste sundag', (2017, 7, 2))])
def test_weekday_ref(text, date):
    assert start(text) == AstroDate(*date)
