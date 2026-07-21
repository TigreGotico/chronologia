"""fy: relative offsets both directions, named days, weekday refs."""
from datetime import timedelta

import pytest

from ._corpus import (ANCHOR, ad, start, start_end, span, nomatch, past,
                      future, AstroDate)


@pytest.mark.parametrize("text,n,unit", [('trije dagen lyn', 3, 'day'), ('ien dei lyn', 1, 'day'), ('twa wiken lyn', 2, 'week'), ('fiif moannen lyn', 5, 'month'), ('ien jier lyn', 1, 'year'), ('tsien jier lyn', 10, 'year'), ('ien oere lyn', 1, 'hour'), ('30 minuten lyn', 30, 'minute'), ('sân dagen lyn', 7, 'day')])
def test_past(text, n, unit):
    assert start_end(text) == past(n, unit)


@pytest.mark.parametrize("text,n,unit", [('oer trije dagen', 3, 'day'), ('oer twa wiken', 2, 'week'), ('oer ien moanne', 1, 'month'), ('oer tsien jier', 10, 'year'), ('oer ien oere', 1, 'hour'), ('oer 30 minuten', 30, 'minute'), ('oer fjouwer dagen', 4, 'day'), ('oer ien jier', 1, 'year')])
def test_future(text, n, unit):
    assert start_end(text) == future(n, unit)


@pytest.mark.parametrize("text,off", [('hjoed', 0), ('juster', -1), ('moarn', 1), ('eargister', -2), ('oaremoarn', 2)])
def test_named_day(text, off):
    day = (ANCHOR + timedelta(days=off)).replace(hour=0, minute=0)
    assert start(text) == ad(day)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,date", [('oare moandei', (2017, 7, 3)), ('ôfrûne freed', (2017, 6, 23)), ('oare tiisdei', (2017, 7, 4)), ('ôfrûne moandei', (2017, 6, 26)), ('oare snein', (2017, 7, 2))])
def test_weekday_ref(text, date):
    assert start(text) == AstroDate(*date)
