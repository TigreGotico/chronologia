# -*- coding: utf-8 -*-
"""BUG (strict xfail): "в <month-prepositional> <year>" silently drops the month.

"в марте 2020" means *March 2020* -- a one-month span [2020-03-01, 2020-04-01).
The engine instead reads only the trailing year and returns the WHOLE year
[2020-01-01, 2021-01-01), silently discarding the prepositional month.  This is
the same silent-year failure mode the dotted-date file guards against: the
caller gets a confident whole-year span with nothing signalling that the month
was lost.

The plain nominative "март 2020" reads correctly as March 2020, so the defect
is specific to the "в" + prepositional-case month surface.  Gold below is the
correct month span; the tests are strict xfails so they will start FAILING (and
flag the regression-to-correct) the moment the engine learns this surface.

Reproduction (anchor 2017-06-27):
    extract_timespan("в марте 2020", "ru", anchor)
      got:  (2020-01-01, 2021-01-01)   whole year
      want: (2020-03-01, 2020-04-01)   March 2020
"""
import pytest

from ._corpus import AstroDate, start_end

# (text, month-prepositional -> month number, year)
_CASES = [
    ("в январе 2020", 1, 2020),
    ("в марте 2020", 3, 2020),
    ("в июне 2019", 6, 2019),
    ("в июле 2021", 7, 2021),
    ("в декабре 2021", 12, 2021),
]


def _end(y, m):
    if m == 12:
        return AstroDate(y + 1, 1, 1)
    return AstroDate(y, m + 1, 1)


@pytest.mark.parametrize("text,m,y", _CASES, ids=[c[0] for c in _CASES])
def test_prep_month_year_should_be_that_month(text, m, y):
    st, en = start_end(text)
    assert st == AstroDate(y, m, 1), text
    assert en == _end(y, m), text
