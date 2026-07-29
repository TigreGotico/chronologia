# -*- coding: utf-8 -*-
"""Slovak last-weekday-of-month with a locative month scope.

"posledný piatok v júni" = the last Friday *of* June.  The month scope is the
locative preposition "v"/"vo" + the locative month name ("v júni", "v marci"),
exactly the connector #354 wired for the ordinal-weekday case.  The "last"
determiner is the adjective "posledný" in full concord with the weekday's
gender ("posledná nedeľa", "posledné" …); its paradigm is vzor *pekný*
(Jazykovedný ústav Ľ. Štúra SAV, Morfológia slovenského jazyka).

Gold is independent calendar arithmetic; anchor Tuesday 2017-06-27 13:04.
"""
from calendar import monthrange
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end


def _day(y, m, d):
    nxt = date(y, m, d) + timedelta(days=1)
    return AstroDate(y, m, d), AstroDate(nxt.year, nxt.month, nxt.day)


def _last_weekday(y, m, weekday):
    last = monthrange(y, m)[1]
    d = date(y, m, last)
    return d.replace(day=last - ((d.weekday() - weekday) % 7))


# weekday: Mon=0 … Sun=6
_CASES = [
    ("posledný piatok v júni", 2017, 6, 4),            # last Fri of June 2017
    ("posledná nedeľa v októbri 2021", 2021, 10, 6),   # last Sun of Oct 2021
    ("posledný pondelok v marci 2020", 2020, 3, 0),    # last Mon of Mar 2020
    ("posledná streda v apríli 2019", 2019, 4, 2),     # last Wed of Apr 2019
    ("posledný štvrtok v januári 2020", 2020, 1, 3),   # last Thu of Jan 2020
]


@pytest.mark.parametrize("text,y,m,wd", _CASES)
def test_last_weekday_of_month_locative(text, y, m, wd):
    d = _last_weekday(y, m, wd)
    assert start_end(text) == _day(d.year, d.month, d.day)


def test_ordinal_weekday_still_binds():
    # regression: #354 ordinal-weekday locative must stay intact
    d = date(2020, 3, 1)
    first = (0 - d.weekday()) % 7
    dd = date(2020, 3, 1 + first + 7 * 2)  # 3rd Monday
    assert start_end("tretí pondelok v marci 2020") == _day(dd.year, dd.month, dd.day)
