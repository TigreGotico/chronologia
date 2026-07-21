"""nn: scope units, half periods, hemisphere-aware seasons, fuzzy months."""
import pytest

from ._corpus import start, start_end, span, nomatch, AstroDate


@pytest.mark.parametrize("text,y0,y1", [('det tredje hundreåret', 200, 300), ('det fyrste hundreåret', 1, 101), ('det 21. hundreåret', 2000, 2100), ('det 20. hundreåret', 1900, 2000), ('det andre årtusenet', 1000, 2000)])
def test_scope_units(text, y0, y1):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y1, 1, 1))


@pytest.mark.parametrize("text,s,e", [('fyrste halvdel av 2020', (2020, 1, 1), (2020, 7, 1)), ('andre halvdel av 2020', (2020, 7, 1), (2021, 1, 1)), ('fyrste halvdel av hundreåret', (2000, 1, 1), (2050, 1, 1))])
def test_half_period(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text,s,e", [('sommar 2020', (2020, 6, 1), (2020, 9, 1)), ('vår 2021', (2021, 3, 1), (2021, 6, 1)), ('vinter 2020', (2020, 12, 1), (2021, 3, 1)), ('haust 2019', (2019, 9, 1), (2019, 12, 1))])
def test_season_of_year(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text,s,e", [('neste sommar', (2018, 6, 1), (2018, 9, 1)), ('neste vinter', (2017, 12, 1), (2018, 3, 1)), ('denne sommar', (2017, 6, 1), (2017, 9, 1))])
def test_season_relative(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text,sm,end", [('byrjinga av juni', (2017, 6), (2017, 6, 11)), ('slutten av desember', (2017, 12), (2018, 1, 1))])
def test_fuzzy_month(text, sm, end):
    s = span(text)
    assert (s.start.year, s.start.month) == sm
    assert s.end == AstroDate(*end)
    assert s.start < s.end
