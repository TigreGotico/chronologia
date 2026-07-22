# -*- coding: utf-8 -*-
"""Holiday references (cs) -- ``holiday_ref``.

Anchor 2017-06-27; a bare holiday resolves to its next occurrence on or after
the anchor. Movable Easter-cycle dates are hand-derived from an INDEPENDENT
computus (dateutil EASTER_WESTERN cycle): Easter 2018 = 2018-04-01. Western computus (Gregorian Easter).
Fixed/tabulated feasts (halloween, valentine, chinese new year, ...) match the
shared registry values cross-checked against the ca corpus. Each date derived
without touching the parser."""
from datetime import timedelta
import pytest
from ._corpus import AstroDate, parse, span, start, nomatch

_BARE = [('nový rok', (2018, 1, 1)), ('vánoce', (2017, 12, 25)), ('štědrý den', (2017, 12, 24)), ('tři králové', (2018, 1, 6)), ('velikonoce', (2018, 4, 1)), ('velký pátek', (2018, 3, 30)), ('velikonoční pondělí', (2018, 4, 2)), ('všech svatých', (2017, 11, 1)), ('halloween', (2017, 10, 31)), ('valentýn', (2018, 2, 14)), ('masopust', (2018, 2, 13)), ('čínský nový rok', (2018, 2, 16))]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("velikonoce 2020", (2020, 4, 12)),
    ("nový rok 2020", (2020, 1, 1)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text", ['cena vajec vzrostla', 'pracovní schůzka'])
def test_no_holiday_no_match(text):
    nomatch(text)
