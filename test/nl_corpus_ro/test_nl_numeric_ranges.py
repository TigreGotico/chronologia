# -*- coding: utf-8 -*-
"""Romanian numeric day ranges inside a named month/year.

Three idiomatic surfaces name the same inclusive day range:
  * "D1-D2 <month> <year>"
  * "de la D1 la D2 <month> <year>"
  * "între D1 și D2 <month> <year>"

The span is half-open ``[(y, m, D1), (y, m, D2+1))`` -- an inclusive D1..D2 span
of ``D2 - D1 + 1`` days. Gold is the day arithmetic itself, computed here and
never read back from the parser. Explicit years are used throughout so the
resolved year is never in doubt.
"""
from datetime import date, timedelta

import pytest

from ._corpus import start_end, AstroDate


_MONTH = {
    2: "februarie", 3: "martie", 5: "mai", 6: "iunie",
    9: "septembrie", 11: "noiembrie",
}
_PAIRS = [(5, 12), (1, 15), (10, 20), (3, 9), (2, 28)]


def _cases():
    out = []
    for y in (2020, 2021):
        for m in _MONTH:
            for d1, d2 in _PAIRS:
                out.append((f"{d1}-{d2} {_MONTH[m]} {y}", y, m, d1, d2))
                out.append((f"de la {d1} la {d2} {_MONTH[m]} {y}", y, m, d1, d2))
                out.append((f"între {d1} și {d2} {_MONTH[m]} {y}", y, m, d1, d2))
    return out


@pytest.mark.parametrize("text,y,m,d1,d2", _cases())
def test_numeric_range(text, y, m, d1, d2):
    end = date(y, m, d2) + timedelta(days=1)
    s, e = start_end(text)
    assert s == AstroDate(y, m, d1), text
    assert e == AstroDate(end.year, end.month, end.day), text
