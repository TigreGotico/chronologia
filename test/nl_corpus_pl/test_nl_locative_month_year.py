# -*- coding: utf-8 -*-
"""Locative month + year in Polish: "w marcu 2019".

Polish names a month under the preposition "w"/"we" in the locative case
(miejscownik: "w marcu", not "w marzec).  "w marcu 2019" means *March 2019* --
the one-month span [2019-03-01, 2019-04-01) -- exactly as the nominative
"marzec 2019" does.  Gold spans are computed by hand, independently of the
parser.
"""
import pytest

from ._corpus import AstroDate, start_end

# (text, month number, year) -- month name is the locative-case surface.
_CASES = [
    ("w styczniu 2020", 1, 2020),
    ("w lutym 2018", 2, 2018),
    ("w marcu 2019", 3, 2019),
    ("w kwietniu 2022", 4, 2022),
    ("w maju 2020", 5, 2020),
    ("w czerwcu 2019", 6, 2019),
    ("w lipcu 2021", 7, 2021),
    ("w sierpniu 2016", 8, 2016),
    ("we wrześniu 2023", 9, 2023),
    ("w październiku 2015", 10, 2015),
    ("w listopadzie 2024", 11, 2024),
    ("w grudniu 2021", 12, 2021),
]


def _end(y, m):
    return AstroDate(y + 1, 1, 1) if m == 12 else AstroDate(y, m + 1, 1)


@pytest.mark.parametrize("text,m,y", _CASES, ids=[c[0] for c in _CASES])
def test_locative_month_year_is_that_month(text, m, y):
    st, en = start_end(text)
    assert st == AstroDate(y, m, 1), text
    assert en == _end(y, m), text
