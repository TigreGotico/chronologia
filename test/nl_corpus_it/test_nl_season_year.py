# -*- coding: utf-8 -*-
"""Italian season with an explicit year, including the "del" idiom:
"la primavera del 2019", "l'estate del 2020".

Meteorological northern-hemisphere quarters (same convention as the existing
seasons file): primavera Mar-Jun, estate Jun-Sep, autunno Sep-Dec, inverno
Dec-Mar (crossing into the following year). The year names the season's own
opening year; inverno therefore ends in year+1. Boundaries by hand.
"""
import pytest

from ._corpus import start_end, AstroDate

# (text, expected start, expected end)
_CASES = [
    ("la primavera del 2019", AstroDate(2019, 3, 1), AstroDate(2019, 6, 1)),
    ("l'estate del 2020", AstroDate(2020, 6, 1), AstroDate(2020, 9, 1)),
    ("l'autunno del 2015", AstroDate(2015, 9, 1), AstroDate(2015, 12, 1)),
    ("l'inverno del 2000", AstroDate(2000, 12, 1), AstroDate(2001, 3, 1)),
    ("la primavera del 1999", AstroDate(1999, 3, 1), AstroDate(1999, 6, 1)),
    ("l'estate del 1969", AstroDate(1969, 6, 1), AstroDate(1969, 9, 1)),
    # bare "<season> <year>" without "del" agrees with the "del" form
    ("primavera 2019", AstroDate(2019, 3, 1), AstroDate(2019, 6, 1)),
    ("estate 2020", AstroDate(2020, 6, 1), AstroDate(2020, 9, 1)),
    ("inverno 1889", AstroDate(1889, 12, 1), AstroDate(1890, 3, 1)),
]


@pytest.mark.parametrize("text,s,e", _CASES)
def test_season_of_year(text, s, e):
    assert start_end(text) == (s, e)


def test_del_and_bare_forms_agree():
    assert start_end("l'autunno del 2015") == start_end("autunno 2015")
