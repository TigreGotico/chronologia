"""Finnish month+year ("tammikuu 2022") -> the whole calendar month.

The nominative month name plus a year names the month; the span runs from
the 1st to the 1st of the following month.  Oracle is independent calendar
arithmetic.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end

_NOM = [
    None, "tammikuu", "helmikuu", "maaliskuu", "huhtikuu", "toukokuu",
    "kesäkuu", "heinäkuu", "elokuu", "syyskuu", "lokakuu", "marraskuu",
    "joulukuu",
]

_YEARS = [1999, 2010, 2020, 2033]

_CASES = [
    (f"{_NOM[mo]} {y}", y, mo)
    for y in _YEARS
    for mo in range(1, 13)
]


@pytest.mark.parametrize("text,y,mo", _CASES)
def test_month_year(text, y, mo):
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, 1))
    ey, emo = (y + 1, 1) if mo == 12 else (y, mo + 1)
    assert e == ad(datetime(ey, emo, 1))
