# -*- coding: utf-8 -*-
"""Second-pass sweep: Slovak calendar quarters and ISO weeks, fresh years.

test_nl_quarter.py only spot-checks a handful of years (2018-2020, 2026);
this sweep runs all four quarters, both the "Qn" and dotted-ordinal
"n. kvartál" surfaces, across 8 fresh years. test_nl_iso_week.py only
spot-checks a handful of (year, week) pairs; this sweep runs 8 weeks spread
across the year for 4 fresh years. Quarter bounds and ISO-week Mondays are
computed independently (plain month arithmetic; ``date.fromisocalendar``),
never read from the parser."""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

_Q_YEARS = (2001, 2005, 2011, 2016, 2022, 2027, 2031, 2036)


def _quarter_span(y, q):
    sm = 3 * (q - 1) + 1
    em = sm + 3
    ey = y
    if em > 12:
        em -= 12
        ey += 1
    return AstroDate(y, sm, 1), AstroDate(ey, em, 1)


@pytest.mark.parametrize("year", _Q_YEARS)
@pytest.mark.parametrize("q", (1, 2, 3, 4))
def test_quarter_q_form_fresh_year(q, year):
    assert start_end(f"Q{q} {year}") == _quarter_span(year, q)


@pytest.mark.parametrize("year", _Q_YEARS)
@pytest.mark.parametrize("q", (1, 2, 3, 4))
def test_quarter_dotted_ordinal_fresh_year(q, year):
    assert start_end(f"{q}. kvartál {year}") == _quarter_span(year, q)


_ISO_YEARS = (2016, 2021, 2027, 2032)
_ISO_WEEKS = (2, 9, 15, 21, 28, 35, 41, 48)


@pytest.mark.parametrize("week", _ISO_WEEKS)
@pytest.mark.parametrize("year", _ISO_YEARS)
def test_iso_week_fresh(year, week):
    mon = date.fromisocalendar(year, week, 1)
    nxt = mon + timedelta(days=7)
    assert start_end(f"týždeň {week} {year}") == (
        AstroDate(mon.year, mon.month, mon.day),
        AstroDate(nxt.year, nxt.month, nxt.day))
