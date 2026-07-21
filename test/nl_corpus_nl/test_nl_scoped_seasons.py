"""nl: scope units, half periods, hemisphere-aware seasons, fuzzy months."""
import pytest

from ._corpus import start, start_end, span, nomatch, AstroDate


@pytest.mark.parametrize("text,y0,y1", [('de derde eeuw', 200, 300), ('de eerste eeuw', 1, 101), ('de 21e eeuw', 2000, 2100), ('de 20e eeuw', 1900, 2000), ('het tweede millennium', 1000, 2000)])
def test_scope_units(text, y0, y1):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y1, 1, 1))


@pytest.mark.parametrize("text,s,e", [('de eerste helft van 2020', (2020, 1, 1), (2020, 7, 1)), ('de tweede helft van 2020', (2020, 7, 1), (2021, 1, 1)), ('de eerste helft van de eeuw', (2000, 1, 1), (2050, 1, 1))])
def test_half_period(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text,s,e", [('zomer 2020', (2020, 6, 1), (2020, 9, 1)), ('lente 2021', (2021, 3, 1), (2021, 6, 1)), ('winter 2020', (2020, 12, 1), (2021, 3, 1)), ('herfst 2019', (2019, 9, 1), (2019, 12, 1))])
def test_season_of_year(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text,s,e", [('volgende zomer', (2018, 6, 1), (2018, 9, 1)), ('volgende winter', (2017, 12, 1), (2018, 3, 1)), ('deze zomer', (2017, 6, 1), (2017, 9, 1))])
def test_season_relative(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text,sm,end", [('begin juni', (2017, 6), (2017, 6, 11)), ('eind december', (2017, 12), (2018, 1, 1))])
def test_fuzzy_month(text, sm, end):
    s = span(text)
    assert (s.start.year, s.start.month) == sm
    assert s.end == AstroDate(*end)
    assert s.start < s.end
