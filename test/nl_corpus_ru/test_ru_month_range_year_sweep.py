# -*- coding: utf-8 -*-
"""Closed month range with an explicit year (ru) -- "с января по март 2020".

"с <month> по <month> <year>" is an inclusive whole-month range: the span runs
[first-month/1 00:00, (last-month+1)/1 00:00) within the stated year, with the
December end rolling to 1 January of the next year.  Gold is that rule applied
by independent arithmetic.  Anchor 2017-06-27.

The genitive-after-"с" / accusative-after-"по" surfaces coincide with the bare
genitive month names used here, which the engine accepts.
"""
import pytest

from ._corpus import AstroDate, start_end

_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

# (first-month, last-month) inclusive pairs, first < last
_PAIRS = [(1, 3), (2, 5), (3, 6), (4, 8), (5, 8), (6, 11), (9, 12), (1, 12),
          (7, 10), (10, 12)]
_YEARS = (2018, 2019, 2020, 2021)


def _end_ad(y, last):
    if last == 12:
        return AstroDate(y + 1, 1, 1)
    return AstroDate(y, last + 1, 1)


def _cases():
    out = []
    for m1, m2 in _PAIRS:
        for y in _YEARS:
            text = f"с {_MONTHS_GEN[m1]} по {_MONTHS_GEN[m2]} {y}"
            out.append((text, y, m1, m2))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,y,m1,m2", _CASES, ids=[c[0] for c in _CASES])
def test_month_range_with_year(text, y, m1, m2):
    st, en = start_end(text)
    assert st == AstroDate(y, m1, 1), text
    assert en == _end_ad(y, m2), text
