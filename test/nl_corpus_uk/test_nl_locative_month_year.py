# -*- coding: utf-8 -*-
"""Locative month + year in Ukrainian: "у березні 2019".

Ukrainian names a month under the preposition "у"/"в" in the locative case
("у березні", not "у березень").  "у березні 2019" means *March 2019* -- the
one-month span [2019-03-01, 2019-04-01) -- exactly as the nominative
"березень 2019" does.  Gold spans are computed by hand, independently of the
parser.
"""
import pytest

from ._corpus import AstroDate, start_end

# (text, month number, year) -- month name is the locative-case surface.
_CASES = [
    ("у січні 2020", 1, 2020),
    ("у лютому 2018", 2, 2018),
    ("у березні 2019", 3, 2019),
    ("у квітні 2022", 4, 2022),
    ("у травні 2020", 5, 2020),
    ("у червні 2019", 6, 2019),
    ("у липні 2021", 7, 2021),
    ("у серпні 2016", 8, 2016),
    ("у вересні 2023", 9, 2023),
    ("у жовтні 2015", 10, 2015),
    ("у листопаді 2024", 11, 2024),
    ("в грудні 2021", 12, 2021),
]


def _end(y, m):
    return AstroDate(y + 1, 1, 1) if m == 12 else AstroDate(y, m + 1, 1)


@pytest.mark.parametrize("text,m,y", _CASES, ids=[c[0] for c in _CASES])
def test_locative_month_year_is_that_month(text, m, y):
    st, en = start_end(text)
    assert st == AstroDate(y, m, 1), text
    assert en == _end(y, m), text
