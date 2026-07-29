# -*- coding: utf-8 -*-
"""Second-pass sweep: Greek fixed-date feasts across a fresh set of years.

``test_el_holiday_year_sweep.py`` already swept the plain word-form feasts
(Πρωτοχρονιά / Θεοφάνεια / Χριστούγεννα) over 1990-2025 and deliberately
skipped the ordinal-day national holidays ("25η Μαρτίου", "28η Οκτωβρίου"),
noting the ordinal-day pattern was believed unbound. Re-probing shows those
two dates DO bind correctly (they are hardcoded fixed feasts, unlike the
generic "Nη <month-gen> <year>" pattern which is still broken for arbitrary
days -- confirmed separately and left untouched here). This file:

* re-verifies the three word-form feasts over 20 YEARS NOT already covered
  by the first sweep, plus a fourth word-form feast (Πρωτομαγιά / May Day)
  that the first sweep never touched at all;
* adds the two ordinal-day national holidays over the same fresh years.

Gold is the constant (month, day) placed in the requested year -- independent
arithmetic, never the parser's own output.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import span, start

A = datetime(2017, 6, 27, 13, 4)

# word-form feast -> fixed (month, day); Πρωτομαγιά is net-new vs. the first sweep
WORD_FEASTS = {
    "πρωτοχρονιά": (1, 1),
    "θεοφάνεια": (1, 6),
    "χριστούγεννα": (12, 25),
    "πρωτομαγιά": (5, 1),
}

# ordinal-day national holidays -- explicitly excluded from the first sweep
ORDINAL_FEASTS = {
    "25η μαρτίου": (3, 25),
    "28η οκτωβρίου": (10, 28),
}

# fresh years, disjoint from the first sweep's 1990/2000/2010/2018-2025 span
_YEARS = [1885, 1897, 1901, 1913, 1927, 1934, 1946, 1958, 1963, 1971,
          1980, 1988, 1993, 2005, 2011, 2016, 2027, 2028, 2031, 2035]

_WORD_CASES = [
    (f"{name} {y}", y, mo, d)
    for name, (mo, d) in WORD_FEASTS.items() for y in _YEARS
]

_ORDINAL_CASES = [
    (f"{name} {y}", y, mo, d)
    for name, (mo, d) in ORDINAL_FEASTS.items() for y in _YEARS
]


@pytest.mark.parametrize("text,y,mo,d", _WORD_CASES)
def test_word_form_feast_fresh_years(text, y, mo, d):
    assert start(text, A) == AstroDate(y, mo, d)
    assert span(text, A).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,mo,d", _ORDINAL_CASES)
def test_ordinal_national_holiday_fresh_years(text, y, mo, d):
    assert start(text, A) == AstroDate(y, mo, d)
    assert span(text, A).width == timedelta(days=1)
