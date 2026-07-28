# -*- coding: utf-8 -*-
"""Oracle sweep: DAY MONTH YEAR across all twelve Gregorian months in both the
Gulf/Egyptian (يناير…ديسمبر) and Levantine (كانون الثاني…كانون الأول) naming
systems, in Western and Arabic-Indic digits.  Gold is a single civil day
[Y-M-D, Y-M-D+1) derived by independent arithmetic, never the parser."""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

# month number -> (Gulf name, Levantine name)
MONTHS = {
    1: ("يناير", "كانون الثاني"),
    2: ("فبراير", "شباط"),
    3: ("مارس", "آذار"),
    4: ("أبريل", "نيسان"),
    5: ("مايو", "أيار"),
    6: ("يونيو", "حزيران"),
    7: ("يوليو", "تموز"),
    8: ("أغسطس", "آب"),
    9: ("سبتمبر", "أيلول"),
    10: ("أكتوبر", "تشرين الأول"),
    11: ("نوفمبر", "تشرين الثاني"),
    12: ("ديسمبر", "كانون الأول"),
}

# (day, year) pairs valid in every month
DAY_YEARS = [(3, 2019), (15, 2020), (28, 1999), (1, 2033), (22, 1948)]

_WEST = "0123456789"
_ARIND = "٠١٢٣٤٥٦٧٨٩"


def _arabic_indic(n):
    return "".join(_ARIND[_WEST.index(c)] for c in str(n))


def _cases():
    out = []
    for m, (gulf, lev) in MONTHS.items():
        for d, y in DAY_YEARS:
            s = date(y, m, d)
            e = s + timedelta(days=1)
            for name in (gulf, lev):
                out.append((f"{d} {name} {y}", s, e))
            # Arabic-Indic digits with the Gulf name
            out.append((f"{_arabic_indic(d)} {gulf} {_arabic_indic(y)}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_full_date_sweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
