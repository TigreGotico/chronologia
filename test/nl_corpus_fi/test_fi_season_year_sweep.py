"""Finnish meteorological season + year across many years.

kevät (spring) = Mar-May, kesä (summer) = Jun-Aug, syksy (autumn) = Sep-Nov,
talvi (winter) = Dec-Feb (wraps into the next year).  Span is the three-month
block; oracle is independent arithmetic.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end

# season -> (start-month, end-month) ; talvi's end-month is in the next year
_SEASON = {
    "kevät": (3, 6),
    "kesä": (6, 9),
    "syksy": (9, 12),
    "talvi": (12, 3),
}

_YEARS = list(range(2018, 2026))

_CASES = [
    (f"{name} {y}", y, name)
    for y in _YEARS
    for name in _SEASON
]


@pytest.mark.parametrize("text,y,name", _CASES)
def test_season_year(text, y, name):
    smo, emo = _SEASON[name]
    s, e = start_end(text)
    assert s == ad(datetime(y, smo, 1))
    ey = y + 1 if emo < smo else y
    assert e == ad(datetime(ey, emo, 1))
