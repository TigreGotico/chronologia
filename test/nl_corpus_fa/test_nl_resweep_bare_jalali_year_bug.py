# -*- coding: utf-8 -*-
"""Native-reviewer bug ledger for Persian -- bare year reads Solar-Hijri.

FIXED: a bare 4-digit year (``1402``, optionally headed by ``سال``) is read on
the PRIMARY Solar-Hijri calendar, not literal Gregorian.  fa is dual-calendar
and the corpus's own documentation (``_corpus.py``) states Solar Hijri is
primary; a lone year like ``1402`` in Persian text is naturally read as 1402 SH
(Gregorian span 2023-03-21..2024-03-21 per the independent Borkowski oracle in
``_jalali``), not literal Gregorian year 1402 AD.

The bare-year reading is bounded to the civil Solar-Hijri window (1200..1500):
Gregorian-scale years like ``2024`` stay Gregorian, and the explicit میلادی
("AD / Gregorian") marker escapes through the separate ``era_ad`` construction
and still reads Gregorian -- both pinned in ``test_nl_bare_jalali_year.py``.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end
from ._jalali import j2g

_CASES = [
    ("1402", 1402),
    ("سال 1402", 1402),
]


@pytest.mark.parametrize("text,y", _CASES)
def test_bare_year_is_solar_hijri(text, y):
    s = j2g(y, 1, 1)
    e = j2g(y + 1, 1, 1)
    got = start_end(text)
    assert got == (ad(datetime(s.year, s.month, s.day)),
                   ad(datetime(e.year, e.month, e.day)))
