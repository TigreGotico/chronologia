# -*- coding: utf-8 -*-
"""sv: "början / mitten / slutet av <month> <year>" thirds sweep.

The lib splits a named month into three equal thirds. Because every month
length is a multiple of 3 hours per third only after multiplying by 8
(days_in_month * 8 hours == days_in_month * 24 / 3), the boundaries land on
exact clock times computed here by INDEPENDENT integer arithmetic:

    boundary(k) = first-of-month 00:00 + (days_in_month * 8) * k  hours

början = [boundary0, boundary1), mitten = [boundary1, boundary2),
slutet = [boundary2, boundary3) where boundary3 == first of next month.

Anchor 2017-06-27; year-qualified so no prefer-future roll applies.
"""
import calendar
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, span

_MONTHS = {
    1: "januari", 2: "februari", 3: "mars", 4: "april", 5: "maj", 6: "juni",
    7: "juli", 8: "augusti", 9: "september", 10: "oktober", 11: "november",
    12: "december",
}
_YEARS = [2020, 2021]
_PHASE = {"början": 0, "mitten": 1, "slutet": 2}


def _boundary(year, month, k):
    dim = calendar.monthrange(year, month)[1]
    return datetime(year, month, 1) + timedelta(hours=dim * 8 * k)


def _dt(d):
    return AstroDate(d.year, d.month, d.day, d.hour, d.minute, d.second,
                     d.microsecond)


def _build():
    cases = []
    for phase, k in _PHASE.items():
        for mo in range(1, 13):
            for yr in _YEARS:
                text = f"{phase} av {_MONTHS[mo]} {yr}"
                s = _dt(_boundary(yr, mo, k))
                e = _dt(_boundary(yr, mo, k + 1))
                cases.append((text, s, e))
    return cases


_CASES = _build()


@pytest.mark.parametrize("text,gs,ge", _CASES, ids=[c[0] for c in _CASES])
def test_month_third(text, gs, ge):
    s = span(text)
    assert (s.start, s.end) == (gs, ge)
    assert s.start < s.end
