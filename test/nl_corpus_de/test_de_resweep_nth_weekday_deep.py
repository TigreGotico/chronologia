# -*- coding: utf-8 -*-
"""Second-pass deep sweep of the German ordinal-weekday-of-month idiom
"der <ordinal> <Wochentag> im <Monat> <Jahr>", widened past the original
corpus's 2018-2021 sample: this file drives the FULL grid of 7 weekdays x
4 cardinal ordinals (erste..vierte) x 12 months x 3 fresh years (2023, 2025,
2027 -- none overlap the original file's years), plus the "letzte" (last
occurrence) ordinal for every weekday x month x year in the same grid.

The oracle is independent calendar arithmetic (:func:`_nth_weekday` and
:func:`_last_weekday` walk the month counting matching weekdays); the parser
is never consulted for the gold, only for the pass/fail check that already
ran during corpus construction (every case here is a verified match).

Anchor 2017-06-27 (Dienstag).
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

_WD = {"montag": 0, "dienstag": 1, "mittwoch": 2, "donnerstag": 3,
       "freitag": 4, "samstag": 5, "sonntag": 6}
_ORD = {1: "erste", 2: "zweite", 3: "dritte", 4: "vierte"}
_MO = ["", "januar", "februar", "märz", "april", "mai", "juni", "juli",
       "august", "september", "oktober", "november", "dezember"]
_YEARS = (2023, 2025, 2027)


def _nth_weekday(y, m, wd, n):
    c = 0
    for d in range(1, calendar.monthrange(y, m)[1] + 1):
        if date(y, m, d).weekday() == wd:
            c += 1
            if c == n:
                return date(y, m, d)
    return None


def _last_weekday(y, m, wd):
    for d in range(calendar.monthrange(y, m)[1], 0, -1):
        if date(y, m, d).weekday() == wd:
            return date(y, m, d)
    return None


_CASES = []
for _y in _YEARS:
    for _m in range(1, 13):
        for _wdname, _wdnum in _WD.items():
            for _n in (1, 2, 3, 4):
                _d = _nth_weekday(_y, _m, _wdnum, _n)
                assert _d is not None, (_y, _m, _wdname, _n)
                _CASES.append(
                    (f"der {_ORD[_n]} {_wdname} im {_MO[_m]} {_y}", _d))
            _dl = _last_weekday(_y, _m, _wdnum)
            assert _dl is not None, (_y, _m, _wdname)
            _CASES.append((f"der letzte {_wdname} im {_MO[_m]} {_y}", _dl))


@pytest.mark.parametrize("text,d", _CASES)
def test_nth_weekday_deep_grid(text, d):
    sp = span(text)
    assert sp.start == AstroDate(d.year, d.month, d.day), f"{text!r} -> {sp}"
    nxt = d + timedelta(days=1)
    assert sp.end == AstroDate(nxt.year, nxt.month, nxt.day)


def test_grid_size_sanity():
    # 7 weekdays x 5 ordinals (4 cardinal + letzte) x 12 months x 3 years
    assert len(_CASES) == 7 * 5 * 12 * 3
