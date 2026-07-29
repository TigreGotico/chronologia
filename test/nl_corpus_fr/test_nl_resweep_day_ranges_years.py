# -*- coding: utf-8 -*-
"""Second-pass sweep: closed day-ranges "du N au M <month> <year>" with an
EXPLICIT year, across all twelve months and six years spread over the
2016-2030 span, four random day-pairs per month/year. This complements
test_nl_ranges.py / test_nl_ranges_topup.py, which only exercise the
prefer-future bare-year form.

A closed "du A au B" range is inclusive of B, so the exclusive end is B + 1
day, rolling into the first of the following month (or year, for December)
when B is the last day of the month. Gold is computed here with plain
calendar arithmetic (``calendar.monthrange``), never read back from the
parser.
"""
import calendar
import random

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end


_MONTHS = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre",
    12: "décembre",
}

_YEARS = [2016, 2019, 2021, 2023, 2026, 2030]


def _sweep():
    rng = random.Random(42)
    out = []
    for y in _YEARS:
        for m in _MONTHS:
            maxd = calendar.monthrange(y, m)[1]
            for _ in range(4):
                a = rng.randint(1, maxd - 1)
                b = rng.randint(a + 1, maxd)
                astr = "1er" if a == 1 else str(a)
                text = f"du {astr} au {b} {_MONTHS[m]} {y}"
                gold_s = AstroDate(y, m, a)
                end_day = b + 1
                if end_day > maxd:
                    gold_e = AstroDate(y + 1, 1, 1) if m == 12 else AstroDate(y, m + 1, 1)
                else:
                    gold_e = AstroDate(y, m, end_day)
                out.append((text, gold_s, gold_e))
    return out


@pytest.mark.parametrize("text,gold_s,gold_e", _sweep())
def test_explicit_year_day_range_sweep(text, gold_s, gold_e):
    s, e = start_end(text)
    assert (s, e) == (gold_s, gold_e), f"{text!r} -> {s}..{e}"
