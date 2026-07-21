"""sv: relative offsets both directions, named days, weekday refs."""
from datetime import timedelta

import pytest

from ._corpus import (ANCHOR, ad, start, start_end, span, nomatch, past,
                      future, AstroDate)


@pytest.mark.parametrize("text,n,unit", [('för tre dagar sedan', 3, 'day'), ('för en dag sedan', 1, 'day'), ('för två veckor sedan', 2, 'week'), ('för fem månader sedan', 5, 'month'), ('för ett år sedan', 1, 'year'), ('för tio år sedan', 10, 'year'), ('för en timme sedan', 1, 'hour'), ('för 30 minuter sedan', 30, 'minute'), ('för sju dagar sedan', 7, 'day')])
def test_past(text, n, unit):
    assert start_end(text) == past(n, unit)


@pytest.mark.parametrize("text,n,unit", [('om tre dagar', 3, 'day'), ('om två veckor', 2, 'week'), ('om en månad', 1, 'month'), ('om tio år', 10, 'year'), ('om en timme', 1, 'hour'), ('om 30 minuter', 30, 'minute'), ('om fyra dagar', 4, 'day'), ('om ett år', 1, 'year')])
def test_future(text, n, unit):
    assert start_end(text) == future(n, unit)


@pytest.mark.parametrize("text,off", [('idag', 0), ('igår', -1), ('imorgon', 1), ('förrgår', -2), ('övermorgon', 2)])
def test_named_day(text, off):
    day = (ANCHOR + timedelta(days=off)).replace(hour=0, minute=0)
    assert start(text) == ad(day)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,date", [('nästa måndag', (2017, 7, 3)), ('förra fredagen', (2017, 6, 23)), ('nästa tisdag', (2017, 7, 4)), ('förra måndagen', (2017, 6, 26)), ('nästa söndag', (2017, 7, 2))])
def test_weekday_ref(text, date):
    assert start(text) == AstroDate(*date)
