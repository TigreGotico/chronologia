"""fy: BC/AD (multi-word era vocabulary), deep time, named periods."""
import pytest

from ._corpus import start, span, nomatch, AstroDate


@pytest.mark.parametrize("text,astro_year", [('44 foar kristus', -43), ('44 f.kr.', -43), ('753 foar kristus', -752), ('1 foar kristus', 0), ('100 foar kristus', -99)])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


@pytest.mark.parametrize("text,y", [('2024 nei kristus', 2024), ('2024 n.kr.', 2024), ('1 nei kristus', 1), ('476 nei kristus', 476)])
def test_ad(text, y):
    assert start(text) == AstroDate(y, 1, 1)


@pytest.mark.parametrize("text,approx_year", [('66 miljoen jier lyn', -65998050), ('2 miljoen jier lyn', -1998050), ('3 miljard jier lyn', -2999998050), ('250 miljoen jier lyn', -249998050)])
def test_deep_time(text, approx_year):
    assert start(text).year == approx_year
    assert span(text).start_datetime is None


@pytest.mark.parametrize("text", ['jura', 'kryt', 'trias', 'devoan', 'perm', 'paleozoikum', 'mesozoikum', 'holoseen', 'pleistoseen', 'kambrium', 'brûnstiid', 'izertiid', 'ûnder jura', 'ûnder kryt'])
def test_named_period(text):
    s = span(text)
    assert s.end.year > s.start.year
