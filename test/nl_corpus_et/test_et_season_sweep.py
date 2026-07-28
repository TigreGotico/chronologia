"""Estonian meteorological season + year sweep.

``kevad`` (spring, Mar-Jun), ``suvi`` (summer, Jun-Sep), ``sügis``
(autumn, Sep-Dec) and ``talv`` (winter, Dec-Mar, wrapping the year) each name
a three-month span opening on the first of the start month.  Years are chosen
to avoid overlap with the hand-written season cases already in
``test_et_eras_year_seasons``.  Gold from independent arithmetic.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end

# season -> (start month, end month) ; winter's end wraps to the next year
SEASONS = {
    "kevad": (3, 6),
    "suvi": (6, 9),
    "sügis": (9, 12),
    "talv": (12, 3),
}
YEARS = [2005, 2012, 2018, 2025]


def _cases():
    for y in YEARS:
        for name, (smo, emo) in SEASONS.items():
            yield (f"{name} {y}", y, smo, emo)


CASES = list(_cases())


@pytest.mark.parametrize("text,y,smo,emo", CASES)
def test_season_year(text, y, smo, emo):
    s, e = start_end(text)
    assert s == ad(datetime(y, smo, 1))
    ey = y + 1 if emo <= smo else y
    assert e == ad(datetime(ey, emo, 1))
