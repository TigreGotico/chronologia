# -*- coding: utf-8 -*-
"""Second-pass sweep: closed day-ranges "από N έως M <genitive-month> <year>"
(el) -- e.g. "από 3 έως 18 Απριλίου 2027". ``test_nl_ranges.py`` (shipped)
only covers the open-ended "μέχρι"/"από ... 2010" forms and a bare
month-dash range; this closed within-month numeric range was previously
untested. The span runs [start-day, end-day + 1) within the named month,
independent arithmetic never touching the parser.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start_end

GEN = {
    1: "ιανουαρίου", 2: "φεβρουαρίου", 3: "μαρτίου", 4: "απριλίου",
    5: "μαΐου", 6: "ιουνίου", 7: "ιουλίου", 8: "αυγούστου",
    9: "σεπτεμβρίου", 10: "οκτωβρίου", 11: "νοεμβρίου", 12: "δεκεμβρίου",
}

_YEARS = [1892, 1911, 1936, 1957, 1984, 2009, 2030, 2034]

_CASES = [
    (f"από 3 έως 18 {GEN[mo]} {y}", y, mo, 3, 18)
    for y in _YEARS for mo in range(1, 13)
]


@pytest.mark.parametrize("text,y,mo,d1,d2", _CASES)
def test_closed_day_range_sweep(text, y, mo, d1, d2):
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, d1))
    assert e == ad(datetime(y, mo, d2) + timedelta(days=1))


@pytest.mark.parametrize("text,y,mo,d1,d2", [
    ("από 1 έως 5 Ιανουαρίου 2028", 2028, 1, 1, 5),
    ("από 10 έως 20 Δεκεμβρίου 1999", 1999, 12, 10, 20),
    ("από 6 έως 12 Φεβρουαρίου 2000", 2000, 2, 6, 12),
])
def test_closed_day_range_edges(text, y, mo, d1, d2):
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, d1))
    assert e == ad(datetime(y, mo, d2) + timedelta(days=1))
