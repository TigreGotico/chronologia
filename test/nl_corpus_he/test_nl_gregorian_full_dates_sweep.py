# -*- coding: utf-8 -*-
"""Wide sweep of full Gregorian dates in modern Hebrew: "<day> ב<month> <year>".

The month carries the proclitic ב- inside a full date.  Gold is a one-day span
[Y-M-D, Y-M-D+1) computed by independent :mod:`datetime` arithmetic, never the
parser.  Israel uses Gregorian civil dates in exactly this surface form.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

# month index -> Hebrew name with the ב- proclitic used inside a full date
_MONTHS = {
    1: "בינואר", 2: "בפברואר", 3: "במרץ", 4: "באפריל", 5: "במאי",
    6: "ביוני", 7: "ביולי", 8: "באוגוסט", 9: "בספטמבר", 10: "באוקטובר",
    11: "בנובמבר", 12: "בדצמבר",
}

_DAYS = (1, 7, 15, 22, 28)
_YEARS = (1948, 1969, 2000, 2018, 2024)


def _cases():
    out = []
    for y in _YEARS:
        for m in range(1, 13):
            for d in _DAYS:
                out.append((f"{d} {_MONTHS[m]} {y}", y, m, d))
    return out


@pytest.mark.parametrize("text,y,m,d", _cases())
def test_full_date(text, y, m, d):
    s = date(y, m, d)
    e = s + timedelta(days=1)
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
