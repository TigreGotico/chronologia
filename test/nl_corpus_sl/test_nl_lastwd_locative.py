# -*- coding: utf-8 -*-
"""Slovene last-weekday-of-month with a locative month scope.

"zadnji petek v novembru" = the last Friday *of* November.  The month scope is
the locative preposition "v" + the locative month name ("v novembru", "v
marcu"), the connector #354 wired for the ordinal-weekday case.  The "last"
determiner is the adjective "zadnji" declined in concord ("zadnja", "zadnje");
soft adjectival paradigm (Fran / SSKJ2, ZRC SAZU: zadnji -a -e).

Gold is independent calendar arithmetic; anchor Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start_end

WD = {'ponedeljek': 0, 'torek': 1, 'sreda': 2, 'četrtek': 3, 'petek': 4,
      'sobota': 5, 'nedelja': 6}


def _last_weekday(y, m, weekday):
    nxt = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
    last = nxt - timedelta(days=1)
    offset = (last.weekday() - weekday) % 7
    return last - timedelta(days=offset)


_CASES = [
    ("zadnji petek v novembru 2019", 2019, 11, 'petek'),
    ("zadnji ponedeljek v marcu 2020", 2020, 3, 'ponedeljek'),
    ("zadnja sreda v aprilu 2021", 2021, 4, 'sreda'),
    ("zadnji torek v juniju 2019", 2019, 6, 'torek'),
]


@pytest.mark.parametrize("text,y,m,wd", _CASES)
def test_last_weekday_of_month_locative(text, y, m, wd):
    d0 = _last_weekday(y, m, WD[wd])
    s, e = start_end(text)
    assert s == ad(d0)
    assert e == ad(d0 + timedelta(days=1))


def test_ordinal_weekday_still_binds():
    # regression: #354 ordinal-weekday locative must stay intact
    first = datetime(2020, 3, 1)
    offset = (0 - first.weekday()) % 7
    d0 = first + timedelta(days=offset + 7 * 2)  # 3rd Monday
    s, e = start_end("tretji ponedeljek v marcu 2020")
    assert s == ad(d0)
