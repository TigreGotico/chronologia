# -*- coding: utf-8 -*-
"""Holiday references (uk) -- ``holiday_ref``.

Anchor 2017-06-27; a bare holiday resolves to its next occurrence on or after
the anchor. Movable Easter-cycle dates are hand-derived from an INDEPENDENT
computus (dateutil EASTER_ORTHODOX cycle): Easter 2018 = 2018-04-08. This locale's community follows the Julian paschal cycle, so the Easter surfaces bind the orthodox_easter registry keys.
Fixed/tabulated feasts (halloween, valentine, chinese new year, ...) match the
shared registry values cross-checked against the ca corpus. Each date derived
without touching the parser."""
from datetime import timedelta
import pytest
from ._corpus import AstroDate, parse, span, start, nomatch

_BARE = [('новий рік', (2018, 1, 1)), ('переддень нового року', (2017, 12, 31)), ('великдень', (2018, 4, 8)), ("страсна п'ятниця", (2018, 4, 6)), ('світлий понеділок', (2018, 4, 9)), ('гелловін', (2017, 10, 31)), ('день святого валентина', (2018, 2, 14)), ('китайський новий рік', (2018, 2, 16)), ('рамадан', (2018, 5, 16)), ('ханука', (2017, 12, 13)), ('песах', (2018, 3, 31)), ('новруз', (2018, 3, 21)), ('різдво', (2018, 1, 7)), ('святвечір', (2018, 1, 6))]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("великдень 2020", (2020, 4, 19)),
    ("новий рік 2020", (2020, 1, 1)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text", ['ціна на яйця зросла', 'робоча зустріч'])
def test_no_holiday_no_match(text):
    nomatch(text)
