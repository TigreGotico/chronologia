# -*- coding: utf-8 -*-
"""da: day ranges inside a month.

Two shapes are swept:

  * year-less compact ranges ("fra 5. til 12. juni", "5.-12. juni") -- the
    month rolls to the nearest future occurrence; gold picks the year whose
    start day is on or after the anchor (2017-06-27).
  * explicit-year ranges with the month repeated ("fra 5. juni til 12. juni
    2020").

The range end is exclusive: the last named day plus one.  Gold is arithmetic,
never read from the parser.

The *compact* form with a trailing year ("5.-12. juni 2020") drops the start
day -- a real bug -- so it is pinned xfail rather than fed a wrong gold.
"""
from datetime import date, timedelta

import pytest

from ._corpus import start_end, AstroDate

_ANCHOR = date(2017, 6, 27)
_MONTHS = {3: "marts", 5: "maj", 6: "juni", 8: "august", 10: "oktober"}
_PAIRS = [(1, 5), (3, 9), (5, 12), (10, 20), (12, 25), (2, 28)]


def _future_year(m, d2):
    # the range rolls forward only if its whole extent is behind the anchor,
    # i.e. the last named day is before it
    return 2017 if date(2017, m, d2) >= _ANCHOR else 2018


_COMPACT = []
for _m, _mname in _MONTHS.items():
    for _d1, _d2 in _PAIRS:
        _y = _future_year(_m, _d2)
        _s = AstroDate(_y, _m, _d1)
        _e = AstroDate(_y, _m, _d2) + timedelta(days=1)
        _COMPACT.append((f"fra {_d1}. til {_d2}. {_mname}", _s, _e))
        _COMPACT.append((f"{_d1}.-{_d2}. {_mname}", _s, _e))


@pytest.mark.parametrize("text,s,e", _COMPACT)
def test_compact_range_prefers_future(text, s, e):
    assert start_end(text) == (s, e)


_YEAR = []
for _m, _mname in _MONTHS.items():
    for _yr in (2019, 2020, 2021):
        for _d1, _d2 in _PAIRS:
            _s = AstroDate(_yr, _m, _d1)
            _e = AstroDate(_yr, _m, _d2) + timedelta(days=1)
            _YEAR.append(
                (f"fra {_d1}. {_mname} til {_d2}. {_mname} {_yr}", _s, _e))


@pytest.mark.parametrize("text,s,e", _YEAR)
def test_explicit_year_range(text, s, e):
    assert start_end(text) == (s, e)


@pytest.mark.parametrize("text,s,e", [
    ("5.-12. juni 2020", AstroDate(2020, 6, 5),
     AstroDate(2020, 6, 12) + timedelta(days=1)),
    ("fra 3. til 9. maj 2020", AstroDate(2020, 5, 3),
     AstroDate(2020, 5, 9) + timedelta(days=1)),
])
def test_compact_range_with_year(text, s, e):  # was xfail; fixed by PR #335
    assert start_end(text) == (s, e)
