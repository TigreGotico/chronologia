# -*- coding: utf-8 -*-
"""Second-pass sweep: closed day-of-month range with explicit year (ru),
fresh day-pairs and fresh years -- "с 4 по 14 января 2022".

Round 2 (``test_ru_day_range_year_sweep``) swept ranges (1,10) (5,12) (3,9)
(10,20) (15,25) (2,27) across years 2018..2021.  This file uses five DIFFERENT
day-pairs across FOUR fresh years (2022..2025), so no (text) id collides with
round 1 or round 2.

"с A по B <month>" is an inclusive day-range within one month; the parsed
span runs [A-th 00:00, (B+1)-th 00:00).  Gold is that rule applied by
independent arithmetic.  Anchor 2017-06-27 (module contract; unused for the
explicit-year reading).
"""
import pytest

from ._corpus import AstroDate, start_end

_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

# fresh (start-day, end-day) pairs, disjoint from round 1/2's
_RANGES = [(4, 14), (6, 16), (8, 18), (11, 21), (13, 23)]
# fresh years, disjoint from round 2's (2018, 2019, 2020, 2021)
_YEARS = (2022, 2023, 2024, 2025)


def _cases():
    out = []
    for m in range(1, 13):
        for a, b in _RANGES:
            for y in _YEARS:
                text = f"с {a} по {b} {_MONTHS_GEN[m]} {y}"
                out.append((text, y, m, a, b))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,y,m,a,b", _CASES, ids=[c[0] for c in _CASES])
def test_day_range_with_year_fresh(text, y, m, a, b):
    st, en = start_end(text)
    assert st == AstroDate(y, m, a), text
    # every swept range ends at day <= 23, so (B+1) never overflows the
    # month (even February) -- no rollover arithmetic needed.
    assert en == AstroDate(y, m, b + 1)
