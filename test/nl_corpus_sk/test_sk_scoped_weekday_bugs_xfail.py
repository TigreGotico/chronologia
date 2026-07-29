# -*- coding: utf-8 -*-
"""Slovak month-scoped weekday and locative-month bugs (strict xfail).

Each case below asserts the *correct* span, computed by independent calendar
arithmetic.  They are strict-xfail because the parser on ``dev`` mis-handles the
month scope; when the grammar is fixed these flip to xpass and the strict flag
turns that into a failure, forcing the marker off.  No wrong gold is ever
committed -- the asserted value is the linguistically right answer.

Observed defects (anchor Tuesday 2017-06-27 13:04):

* Locative month "v marci 2020" reads only the year and returns the whole of
  2020, stranding "v marci"; it should name March 2020.
* Ordinal-weekday-of-month "tretí pondelok v marci 2020" reads "pondelok" as a
  bare next-Monday deixis and strands "tretí ... v marci 2020"; it should be
  the 3rd Monday of March 2020 (2020-03-16).
* Last-weekday-of-month "posledný piatok v júni" reads "posledný piatok" as a
  bare last-Friday deixis and strands "v júni"; it should be the last Friday
  of June 2017 (2017-06-30).
"""
from datetime import date, timedelta
from calendar import monthrange

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end


def _day(y, m, d):
    nxt = date(y, m, d) + timedelta(days=1)
    return AstroDate(y, m, d), AstroDate(nxt.year, nxt.month, nxt.day)


def _month(y, m):
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return AstroDate(y, m, 1), AstroDate(ny, nm, 1)


def _nth_weekday(y, m, weekday, n):
    d = date(y, m, 1)
    first = (weekday - d.weekday()) % 7
    dd = date(y, m, 1 + first + 7 * (n - 1))
    return dd


def _last_weekday(y, m, weekday):
    last = monthrange(y, m)[1]
    d = date(y, m, last)
    return d.replace(day=last - ((d.weekday() - weekday) % 7))


@pytest.mark.parametrize("text,y,m", [  # fixed by PR #354 (locative month)
    ("v marci 2020", 2020, 3),
    ("v januári 2019", 2019, 1),
    ("v decembri 2021", 2021, 12),
])
def test_locative_month_year(text, y, m):
    assert start_end(text) == _month(y, m)


@pytest.mark.parametrize("text,y,m,wd,n", [  # fixed by PR #354 (scoped ordinal)
    ("tretí pondelok v marci 2020", 2020, 3, 0, 3),
    ("prvý pondelok v marci 2020", 2020, 3, 0, 1),
    ("druhá streda v apríli 2019", 2019, 4, 2, 2),
])
def test_ordinal_weekday_of_month(text, y, m, wd, n):
    d = _nth_weekday(y, m, wd, n)
    assert start_end(text) == _day(d.year, d.month, d.day)


@pytest.mark.parametrize("text,y,m,wd", [  # fixed: Slovak "posledný" ordlast
    ("posledný piatok v júni", 2017, 6, 4),
    ("posledná nedeľa v októbri 2021", 2021, 10, 6),
    ("posledný pondelok v marci 2020", 2020, 3, 0),
])
def test_last_weekday_of_month(text, y, m, wd):
    d = _last_weekday(y, m, wd)
    assert start_end(text) == _day(d.year, d.month, d.day)
