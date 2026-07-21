"""nl: BC/AD (multi-word era vocabulary), deep time, named periods."""
import pytest

from ._corpus import start, span, nomatch, AstroDate


@pytest.mark.parametrize("text,astro_year", [('44 voor christus', -43), ('44 v.chr.', -43), ('753 voor christus', -752), ('1 voor christus', 0), ('100 voor christus', -99)])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


@pytest.mark.parametrize("text,y", [('2024 na christus', 2024), ('2024 n.chr.', 2024), ('1 na christus', 1), ('476 na christus', 476)])
def test_ad(text, y):
    assert start(text) == AstroDate(y, 1, 1)


@pytest.mark.parametrize("text,approx_year", [('66 miljoen jaar geleden', -65998050), ('2 miljoen jaar geleden', -1998050), ('3 miljard jaar geleden', -2999998050), ('250 miljoen jaar geleden', -249998050)])
def test_deep_time(text, approx_year):
    assert start(text).year == approx_year
    assert span(text).start_datetime is None


@pytest.mark.parametrize("text", ['in de jura', 'in het krijt', 'de trias', 'het devoon', 'het perm', 'het paleozoicum', 'het mesozoicum', 'het holoceen', 'het pleistoceen', 'het cambrium', 'de bronstijd', 'de ijzertijd'])
def test_named_period(text):
    s = span(text)
    assert s.end.year > s.start.year
