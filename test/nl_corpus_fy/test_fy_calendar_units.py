"""fy: this / next / last calendar-unit periods.

dizze (this), oare (next), ôfrûne (last) applied to wike / moanne, plus the
bare-year period.  Weeks are Monday-anchored ISO weeks; spans come from
independent calendar arithmetic against the Tuesday anchor.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, start_end, AstroDate


def _week(rel):
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    mon = base - timedelta(days=base.weekday()) + timedelta(weeks=rel)
    end = mon + timedelta(weeks=1)
    return (AstroDate(mon.year, mon.month, mon.day),
            AstroDate(end.year, end.month, end.day))


@pytest.mark.parametrize("text,rel", [
    ('dizze wike', 0), ('oare wike', 1), ('ôfrûne wike', -1),
])
def test_relative_week(text, rel):
    assert start_end(text) == _week(rel)


@pytest.mark.parametrize("text,y,m", [
    ('dizze moanne', 2017, 6), ('oare moanne', 2017, 7),
    ('ôfrûne moanne', 2017, 5),
])
def test_relative_month(text, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 1)
    assert e == (AstroDate(y + 1, 1, 1) if m == 12 else AstroDate(y, m + 1, 1))


def test_this_year():
    assert start_end('dit jier') == (AstroDate(2017, 1, 1),
                                      AstroDate(2018, 1, 1))
