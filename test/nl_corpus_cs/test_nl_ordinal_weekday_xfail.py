# -*- coding: utf-8 -*-
"""Ordinal-weekday-of-month (cs) -- KNOWN BUG, strict xfail.

"třetí pondělí v březnu 2020" ("the third Monday in March 2020") and its
bare-genitive twin "třetí pondělí března 2020" are the ordinary Czech ways to
name the Nth weekday of a month.  On ``dev`` the parser silently drops both the
month and the weekday: it reads only the ordinal and returns the Nth day of the
anchor week (e.g. 2017-07-03), stranding "pondělí" and "březnu 2020".  The only
surface that resolves is the *ungrammatical* "v + genitive" ("v března"), which
no Czech speaker would write.

Gold is the true Nth weekday of the named month, computed here by independent
calendar arithmetic (calendar.monthrange / weekday walk), never the parser.
These are strict xfails: when the bug is fixed they flip to xpass and this file
must be promoted to plain asserts.
"""
from datetime import datetime, timedelta
import pytest

from ._corpus import AstroDate, start


_MG = {3: "března", 5: "května", 12: "prosince", 1: "ledna", 4: "dubna"}
_LOC = {3: "březnu", 5: "květnu", 12: "prosinci", 1: "lednu", 4: "dubnu"}


def _nth_weekday(y, m, weekday, n):
    d = datetime(y, m, 1)
    count = 0
    while d.month == m:
        if d.weekday() == weekday:
            count += 1
            if count == n:
                return AstroDate(d.year, d.month, d.day)
        d += timedelta(days=1)
    raise AssertionError("no such weekday")


# (ordinal word, n, weekday word, weekday int, month, year)
_CASES = [
    ("třetí", 3, "pondělí", 0, 3, 2020),   # 2020-03-16
    ("první", 1, "pondělí", 0, 1, 2020),   # 2020-01-06
    ("druhé", 2, "úterý", 1, 5, 2021),     # 2021-05-11
    ("čtvrté", 4, "středa", 2, 4, 2022),   # 2022-04-27
    ("první", 1, "neděle", 6, 12, 2022),   # 2022-12-04
]


def _ids(cases, prep):
    return [f"{o} {w} {prep}{m}/{y}" for o, _, w, _, m, y in cases]


@pytest.mark.xfail(reason="ordinal-weekday-of-month drops month+weekday, "
                          "returns Nth day of anchor week (BUG)",
                   strict=True)
@pytest.mark.parametrize("ordw,n,wdw,wd,m,y", _CASES,
                         ids=_ids(_CASES, "v-"))
def test_locative_form(ordw, n, wdw, wd, m, y):
    gold = _nth_weekday(y, m, wd, n)
    assert start(f"{ordw} {wdw} v {_LOC[m]} {y}") == gold


@pytest.mark.xfail(reason="ordinal-weekday-of-month drops month+weekday, "
                          "returns Nth day of anchor week (BUG)",
                   strict=True)
@pytest.mark.parametrize("ordw,n,wdw,wd,m,y", _CASES,
                         ids=_ids(_CASES, "gen-"))
def test_bare_genitive_form(ordw, n, wdw, wd, m, y):
    gold = _nth_weekday(y, m, wd, n)
    assert start(f"{ordw} {wdw} {_MG[m]} {y}") == gold
