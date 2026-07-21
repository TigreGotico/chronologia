"""nl: relative offsets both directions, named days, weekday refs."""
from datetime import timedelta

import pytest

from ._corpus import (ANCHOR, ad, start, start_end, span, nomatch, past,
                      future, AstroDate)


@pytest.mark.parametrize("text,n,unit", [('drie dagen geleden', 3, 'day'), ('een dag geleden', 1, 'day'), ('twee weken geleden', 2, 'week'), ('vijf maanden geleden', 5, 'month'), ('een jaar geleden', 1, 'year'), ('tien jaar geleden', 10, 'year'), ('een uur geleden', 1, 'hour'), ('30 minuten geleden', 30, 'minute'), ('zeven dagen geleden', 7, 'day')])
def test_past(text, n, unit):
    assert start_end(text) == past(n, unit)


@pytest.mark.parametrize("text,n,unit", [('over drie dagen', 3, 'day'), ('over twee weken', 2, 'week'), ('over een maand', 1, 'month'), ('over tien jaar', 10, 'year'), ('over een uur', 1, 'hour'), ('over 30 minuten', 30, 'minute'), ('over vier dagen', 4, 'day'), ('over een jaar', 1, 'year')])
def test_future(text, n, unit):
    assert start_end(text) == future(n, unit)


@pytest.mark.parametrize("text,off", [('vandaag', 0), ('gisteren', -1), ('morgen', 1), ('eergisteren', -2), ('overmorgen', 2)])
def test_named_day(text, off):
    day = (ANCHOR + timedelta(days=off)).replace(hour=0, minute=0)
    assert start(text) == ad(day)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,date", [('volgende maandag', (2017, 7, 3)), ('vorige vrijdag', (2017, 6, 23)), ('deze zondag', (2017, 7, 2)), ('volgende dinsdag', (2017, 7, 4)), ('vorige maandag', (2017, 6, 26)), ('volgende zondag', (2017, 7, 2))])
def test_weekday_ref(text, date):
    assert start(text) == AstroDate(*date)
