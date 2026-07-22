# -*- coding: utf-8 -*-
"""Holiday references (sk) -- ``holiday_ref``.

Anchor 2017-06-27; a bare holiday resolves to its next occurrence on or after
the anchor. Movable Easter-cycle dates are hand-derived from an INDEPENDENT
computus (dateutil EASTER_WESTERN cycle): Easter 2018 = 2018-04-01. Western computus (Gregorian Easter).
Fixed/tabulated feasts (halloween, valentine, chinese new year, ...) match the
shared registry values cross-checked against the ca corpus. Each date derived
without touching the parser."""
from datetime import timedelta
import pytest
from ._corpus import AstroDate, parse, span, start, nomatch

_BARE = [('nový rok', (2018, 1, 1)), ('vianoce', (2017, 12, 25)), ('štedrý deň', (2017, 12, 24)), ('traja králi', (2018, 1, 6)), ('veľká noc', (2018, 4, 1)), ('veľký piatok', (2018, 3, 30)), ('veľkonočný pondelok', (2018, 4, 2)), ('sviatok všetkých svätých', (2017, 11, 1)), ('halloween', (2017, 10, 31)), ('valentín', (2018, 2, 14)), ('fašiangy', (2018, 2, 13)), ('čínsky nový rok', (2018, 2, 16))]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("veľká noc 2020", (2020, 4, 12)),
    ("nový rok 2020", (2020, 1, 1)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text", ['cena vajec vzrástla', 'pracovná schôdzka'])
def test_no_holiday_no_match(text):
    nomatch(text)
