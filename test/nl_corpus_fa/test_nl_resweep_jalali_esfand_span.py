# -*- coding: utf-8 -*-
"""Second-pass resweep: Solar-Hijri bare ``اسفند <year>`` (month 12) spans.

The original ``test_nl_sweep_solar_hijri_monthyear.py`` deliberately swept
only months 1..11, excluding Esfand because its end rolls into the next
Nowruz.  That end IS derivable from the independent Borkowski oracle
(``j2g(y + 1, 1, 1)``) for any concordant year pair, so it is swept here as
its own case -- new coverage, not a duplicate of the excluded range.

Year 1404 is excluded (as elsewhere) because it is the documented borderline
year where the oracle and the engine's calendar disagree by a day; sweeping
Esfand 1403 would touch that same disagreement through its *end* (1 Farvardin
1404), so 1403 is excluded too.  The remaining years are all internally
concordant on both endpoints.
"""
import pytest

from ._corpus import ad, start_end
from ._jalali import JMON, j2g

_YEARS = [1398, 1399, 1400, 1401, 1402, 1405]


@pytest.mark.parametrize("text,y", [(f"{JMON[11]} {y}", y) for y in _YEARS])
def test_esfand_month_year_span(text, y):
    from datetime import datetime
    s = j2g(y, 12, 1)
    e = j2g(y + 1, 1, 1)
    got = start_end(text)
    assert got == (ad(datetime(s.year, s.month, s.day)),
                   ad(datetime(e.year, e.month, e.day)))
