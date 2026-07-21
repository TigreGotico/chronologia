"""da: relative offsets both directions, named days, weekday refs."""
from datetime import timedelta

import pytest

from ._corpus import (ANCHOR, ad, start, start_end, span, nomatch, past,
                      future, AstroDate)


@pytest.mark.parametrize("text,n,unit", [('for tre dage siden', 3, 'day'), ('for en dag siden', 1, 'day'), ('for to uger siden', 2, 'week'), ('for fem måneder siden', 5, 'month'), ('for et år siden', 1, 'year'), ('for ti år siden', 10, 'year'), ('for en time siden', 1, 'hour'), ('for 30 minutter siden', 30, 'minute'), ('for syv dage siden', 7, 'day')])
def test_past(text, n, unit):
    assert start_end(text) == past(n, unit)


@pytest.mark.parametrize("text,n,unit", [('om tre dage', 3, 'day'), ('om to uger', 2, 'week'), ('om en måned', 1, 'month'), ('om ti år', 10, 'year'), ('om en time', 1, 'hour'), ('om 30 minutter', 30, 'minute'), ('om fire dage', 4, 'day'), ('om et år', 1, 'year')])
def test_future(text, n, unit):
    assert start_end(text) == future(n, unit)


@pytest.mark.parametrize("text,off", [('idag', 0), ('igår', -1), ('imorgen', 1), ('forgårs', -2), ('overmorgen', 2)])
def test_named_day(text, off):
    day = (ANCHOR + timedelta(days=off)).replace(hour=0, minute=0)
    assert start(text) == ad(day)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,date", [('næste mandag', (2017, 7, 3)), ('sidste fredag', (2017, 6, 23)), ('næste tirsdag', (2017, 7, 4)), ('sidste mandag', (2017, 6, 26)), ('næste søndag', (2017, 7, 2))])
def test_weekday_ref(text, date):
    assert start(text) == AstroDate(*date)
