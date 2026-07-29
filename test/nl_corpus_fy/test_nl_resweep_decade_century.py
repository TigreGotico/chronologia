# -*- coding: utf-8 -*-
"""Second-pass sweep (fy): relative decade/century periods -- "folgjende
desennium" (next decade), "foarige desennium" (last decade), "dit desennium"
(this decade); "folgjende ieu", "foarige ieu", "dizze ieu". Not previously
parametrized in this corpus's rel_period coverage (only week/month/year
were). Gold by independent floor-division arithmetic against the 2017-06-27
anchor, same rule as ``en``/``nl`` decade/century tests: the containing
decade/century floors to a multiple of 10/100, then shifts by the relative
step.
"""
import pytest

from ._corpus import AstroDate, start_end


@pytest.mark.parametrize("text,y0,y1", [
    ('dit desennium', 2010, 2020),
    ('folgjende desennium', 2020, 2030),
    ('foarige desennium', 2000, 2010),
])
def test_relative_decade(text, y0, y1):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y1, 1, 1))


@pytest.mark.parametrize("text,y0,y1", [
    ('dizze ieu', 2000, 2100),
    ('folgjende ieu', 2100, 2200),
    ('foarige ieu', 1900, 2000),
])
def test_relative_century(text, y0, y1):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y1, 1, 1))
