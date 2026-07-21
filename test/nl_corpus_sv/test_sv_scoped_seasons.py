"""sv: scope units, half periods, hemisphere-aware seasons, fuzzy months."""
import pytest

from ._corpus import start, start_end, span, nomatch, AstroDate


@pytest.mark.parametrize("text,y0,y1", [('det tredje århundradet', 200, 300), ('det första århundradet', 1, 101), ('det 21 århundradet', 2000, 2100), ('det 20 århundradet', 1900, 2000), ('det andra årtusendet', 1000, 2000)])
def test_scope_units(text, y0, y1):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y1, 1, 1))


@pytest.mark.parametrize("text,s,e", [('första hälften av 2020', (2020, 1, 1), (2020, 7, 1)), ('andra hälften av 2020', (2020, 7, 1), (2021, 1, 1)), ('första hälften av seklet', (2000, 1, 1), (2050, 1, 1))])
def test_half_period(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text,s,e", [('sommar 2020', (2020, 6, 1), (2020, 9, 1)), ('vår 2021', (2021, 3, 1), (2021, 6, 1)), ('vinter 2020', (2020, 12, 1), (2021, 3, 1)), ('höst 2019', (2019, 9, 1), (2019, 12, 1))])
def test_season_of_year(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text,s,e", [('nästa sommar', (2018, 6, 1), (2018, 9, 1)), ('nästa vinter', (2017, 12, 1), (2018, 3, 1)), ('denna sommar', (2017, 6, 1), (2017, 9, 1))])
def test_season_relative(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text,sm,end", [('början av juni', (2017, 6), (2017, 6, 11)), ('slutet av december', (2017, 12), (2018, 1, 1))])
def test_fuzzy_month(text, sm, end):
    s = span(text)
    assert (s.start.year, s.start.month) == sm
    assert s.end == AstroDate(*end)
    assert s.start < s.end
