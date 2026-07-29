# -*- coding: utf-8 -*-
"""Locative (prepositional) month + year in Russian: "в марте 2019".

A Russian speaker naming a calendar month with the preposition "в" declines the
month into the prepositional case ("в марте", not "в март").  "в марте 2019"
means *March 2019* -- the one-month span [2019-03-01, 2019-04-01) -- exactly as
the plain nominative "март 2019" does.  Gold spans below are computed by hand,
independently of the parser.
"""
import pytest

from ._corpus import AstroDate, start_end

# (text, month number, year) -- month name is the prepositional-case surface.
_CASES = [
    ("в январе 2020", 1, 2020),
    ("в феврале 2018", 2, 2018),
    ("в марте 2019", 3, 2019),
    ("в апреле 2022", 4, 2022),
    ("в мае 2020", 5, 2020),
    ("в июне 2019", 6, 2019),
    ("в июле 2021", 7, 2021),
    ("в августе 2016", 8, 2016),
    ("в сентябре 2023", 9, 2023),
    ("в октябре 2015", 10, 2015),
    ("в ноябре 2024", 11, 2024),
    ("в декабре 2021", 12, 2021),
]


def _end(y, m):
    return AstroDate(y + 1, 1, 1) if m == 12 else AstroDate(y, m + 1, 1)


@pytest.mark.parametrize("text,m,y", _CASES, ids=[c[0] for c in _CASES])
def test_locative_month_year_is_that_month(text, m, y):
    st, en = start_end(text)
    assert st == AstroDate(y, m, 1), text
    assert en == _end(y, m), text
