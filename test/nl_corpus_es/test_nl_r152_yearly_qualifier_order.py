# -*- coding: utf-8 -*-
"""R152 (es) -- yearly adverb qualifier folding is order-sensitive: a leading
day-of-month qualifier ("el 15") blocks the month qualifier scan ("en junio")
entirely.

See ``test/nl_corpus_en/test_nl_r152_yearly_qualifier_order.py`` for the full
defect writeup. The mechanism is shared (``_yearly_recur_qualifiers`` in
chronologia/extract/nseries.py) -- only the Spanish day-qualifier surface
("el <N>") and month surface ("en <mes>") differ, both already attested in
``test_nl_r149_adverb_recur_qualifiers.py``.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "es"

_CASES = [
    # -- the defect: order must not matter ----------------------------------
    ("anualmente el 15 en junio", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=15", ""),
    ("anualmente en junio el 15", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=15", ""),
    # -- controls: month-only, no explicit day -> uniform BYMONTHDAY=1 ------
    ("anualmente en junio", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    ("cada ano en junio", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    # -- control: bare day, no month -- must keep stranding, no invented
    # month.
    ("anualmente el 1", "FREQ=YEARLY", "el 1"),
    # -- controls: pre-existing sibling readings, unaffected -----------------
    ("mensualmente el 15", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("anualmente", "FREQ=YEARLY", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_yearly_qualifier_folding_is_order_independent_es(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
