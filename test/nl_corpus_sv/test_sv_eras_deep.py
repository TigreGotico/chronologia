"""sv: BC/AD (multi-word era vocabulary), deep time, named periods."""
import pytest

from ._corpus import start, span, nomatch, AstroDate


@pytest.mark.parametrize("text,astro_year", [('44 före kristus', -43), ('44 f.kr.', -43), ('753 före kristus', -752), ('1 före kristus', 0), ('100 före kristus', -99)])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


@pytest.mark.parametrize("text,y", [('2024 efter kristus', 2024), ('2024 e.kr.', 2024), ('1 efter kristus', 1), ('476 efter kristus', 476)])
def test_ad(text, y):
    assert start(text) == AstroDate(y, 1, 1)


@pytest.mark.parametrize("text,approx_year", [('för 66 miljoner år sedan', -65998050), ('för 2 miljoner år sedan', -1998050), ('för 3 miljarder år sedan', -2999998050), ('för 250 miljoner år sedan', -249998050)])
def test_deep_time(text, approx_year):
    assert start(text).year == approx_year
    assert span(text).start_datetime is None


@pytest.mark.parametrize("text", ['jura', 'krita', 'trias', 'devon', 'perm', 'paleozoikum', 'mesozoikum', 'holocen', 'pleistocen', 'kambrium', 'bronsåldern', 'järnåldern', 'under jura', 'under krita'])
def test_named_period(text):
    s = span(text)
    assert s.end.year > s.start.year
