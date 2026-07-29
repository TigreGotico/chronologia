# -*- coding: utf-8 -*-
"""Second-pass resweep: month-thirds (nl), fresh years.

"begin|midden|eind <maand> <jaar>", same shape as
:mod:`test_nl_month_third_sweep` (years 2019-2022) but over fresh years
2029-2033. The named month is the parent span [1st, next-1st); split into
three equal arithmetic thirds by ``timedelta``, independent of the parser.

Anchor 2017-06-27.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, parse, start_end

_MONTHS = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]
_YEARS = [2029, 2030, 2031, 2032, 2033]


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
def test_month_third_resweep(phrase, gs, ge):
    assert start_end(phrase) == (_ad(gs), _ad(ge)), phrase
    assert parse(phrase)[1] == "", phrase
