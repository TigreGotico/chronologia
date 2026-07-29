# -*- coding: utf-8 -*-
"""Sweep of bare month-and-year in Hebrew: "<month> <year>" spans the whole
calendar month.  Bare (no ב- proclitic) is the month-year surface.  Gold is
[Y-M-1, Y-M+1-1) by independent arithmetic."""
from datetime import date

import pytest

from ._corpus import AstroDate, start_end

_MONTHS = {
    1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל", 5: "מאי", 6: "יוני",
    7: "יולי", 8: "אוגוסט", 9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר",
    12: "דצמבר",
}

_YEARS = (1980, 1995, 2005, 2019, 2027, 2033)


def _next_month(y, m):
    return (y + 1, 1) if m == 12 else (y, m + 1)


def _cases():
    out = []
    for y in _YEARS:
        for m in range(1, 13):
            out.append((f"{_MONTHS[m]} {y}", y, m))
    return out


@pytest.mark.parametrize("text,y,m", _cases())
def test_month_year(text, y, m):
    ny, nm = _next_month(y, m)
    ss, ee = start_end(text)
    assert ss == AstroDate(y, m, 1)
    assert ee == AstroDate(ny, nm, 1)
