# -*- coding: utf-8 -*-
"""Month-thirds sweep (nl): "begin|midden|eind <maand> <jaar>".

The named month is the parent span [1st, next-1st); it is split into three
equal arithmetic thirds by ``timedelta`` (the same rule the fuzzy-period
oracle uses). begin = first third, midden = middle third, eind = last third.
Thirds of a 30/31/28/29-day month land on fractional hours -- all derived
here by independent arithmetic, never pinned from the parser.

"half <maand>" is deliberately not tested: it does NOT bind as a third in
this locale (the word is dropped and the whole month is returned).

Anchor 2017-06-27.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, parse, start_end

_MONTHS = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]
_YEARS = [2019, 2020, 2021, 2022]


def _month_bounds(year, mi):
    s = datetime(year, mi, 1)
    e = datetime(year + 1, 1, 1) if mi == 12 else datetime(year, mi + 1, 1)
    return s, e


def _third(s, e, part):
    wd = (e - s) / 3
    edges = {
        "begin": (s, s + wd),
        "midden": (s + wd, s + 2 * wd),
        "eind": (s + 2 * wd, e),
    }[part]
    return edges


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


def _build():
    cases = []
    for y in _YEARS:
        for mi, mname in enumerate(_MONTHS, start=1):
            s, e = _month_bounds(y, mi)
            for part in ("begin", "midden", "eind"):
                gs, ge = _third(s, e, part)
                cases.append((f"{part} {mname} {y}", gs, ge))
    return cases


_CASES = _build()


@pytest.mark.parametrize("phrase,gs,ge", _CASES, ids=[c[0] for c in _CASES])
def test_month_third(phrase, gs, ge):
    assert start_end(phrase) == (_ad(gs), _ad(ge)), phrase
    assert parse(phrase)[1] == "", phrase
