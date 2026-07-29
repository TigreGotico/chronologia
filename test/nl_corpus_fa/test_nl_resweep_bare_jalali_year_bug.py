# -*- coding: utf-8 -*-
"""Native-reviewer bug ledger for Persian -- strict xfail.

BUG: a bare 4-digit year (``1402``, optionally headed by ``سال``) is resolved
as a literal Gregorian year instead of being read on the PRIMARY Solar-Hijri
calendar.  fa is dual-calendar and the corpus's own documentation
(``_corpus.py``) states Solar Hijri is primary; a lone year like ``1402`` in
Persian text is naturally read as 1402 SH (correct Gregorian span
2023-03-21..2024-03-21 per the independent Borkowski oracle in ``_jalali``),
not literal Gregorian year 1402 AD.  The engine currently returns
[1402-01-01, 1403-01-01) -- the wrong calendar entirely.

Marked ``strict=True`` so a future fix (disambiguating the bare-year
construction onto Solar-Hijri) turns this red, graduating it into a plain
passing corpus entry.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end
from ._jalali import j2g

_CASES = [
    ("1402", 1402),
    ("سال 1402", 1402),
]


@pytest.mark.xfail(strict=True, reason="BUG: bare year read as literal Gregorian, not Solar-Hijri")
@pytest.mark.parametrize("text,y", _CASES)
def test_bare_year_should_be_solar_hijri(text, y):
    s = j2g(y, 1, 1)
    e = j2g(y + 1, 1, 1)
    got = start_end(text)
    assert got == (ad(datetime(s.year, s.month, s.day)),
                   ad(datetime(e.year, e.month, e.day)))
