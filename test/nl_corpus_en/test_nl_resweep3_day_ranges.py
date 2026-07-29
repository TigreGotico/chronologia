"""Third-pass resweep: intra-month day ranges phrased as
"from the N to the M of <month> <year>" (plain cardinal numbers, not
ordinals), swept across all 12 months, three day-pair widths, and a fresh
run of years (2041-2059) disjoint from the second-pass resweep's
2010-2025 window and the original file's ordinal-day, no-year forms.

Gold is plain ``date`` arithmetic -- the day-after-the-end civil date,
never the parser's own output.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
    "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12,
}

_YEARS = (2041, 2044, 2047, 2050, 2053, 2056, 2059)

# kept within every month's shortest length (28)
_PAIRS = ((2, 9), (6, 14), (18, 24))


def _cases():
    out = []
    for year in _YEARS:
        for mname, m in _MONTHS.items():
            for d1, d2 in _PAIRS:
                out.append(
                    (f"from the {d1} to the {d2} of {mname} {year}",
                     year, m, d1, d2))
    return out


@pytest.mark.parametrize("text,year,month,d1,d2", _cases())
def test_day_range_from_to_of_year_sweep_2040s2050s(text, year, month, d1, d2):
    s = date(year, month, d1)
    e = date(year, month, d2) + timedelta(days=1)
    assert start_end(text) == (AstroDate(s.year, s.month, s.day),
                               AstroDate(e.year, e.month, e.day))
