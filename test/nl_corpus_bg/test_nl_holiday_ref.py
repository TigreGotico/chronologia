# -*- coding: utf-8 -*-
"""Holiday references (bg) -- ``holiday_ref``.

Anchor 2017-06-27; a bare holiday resolves to its next occurrence on or after
the anchor. Movable Easter-cycle dates are hand-derived from an INDEPENDENT
computus (dateutil EASTER_ORTHODOX cycle): Easter 2018 = 2018-04-08. This locale's community follows the Julian paschal cycle, so the Easter surfaces bind the orthodox_easter registry keys.
Fixed/tabulated feasts (halloween, valentine, chinese new year, ...) match the
shared registry values cross-checked against the ca corpus. Each date derived
without touching the parser."""
from datetime import timedelta
import pytest
from ._corpus import AstroDate, parse, span, start, nomatch

_BARE = [('нова година', (2018, 1, 1)), ('навечерие на нова година', (2017, 12, 31)), ('великден', (2018, 4, 8)), ('разпети петък', (2018, 4, 6)), ('велики понеделник', (2018, 4, 9)), ('хелоуин', (2017, 10, 31)), ('свети валентин', (2018, 2, 14)), ('китайска нова година', (2018, 2, 16)), ('рамазан', (2018, 5, 16)), ('ханука', (2017, 12, 13)), ('песах', (2018, 3, 31)), ('навруз', (2018, 3, 21))]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("великден 2020", (2020, 4, 19)),
    ("нова година 2020", (2020, 1, 1)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text", ['цената на яйцата се повиши', 'служебна среща'])
def test_no_holiday_no_match(text):
    nomatch(text)
