# -*- coding: utf-8 -*-
"""R152 (de) -- yearly adverb qualifier folding is order-sensitive: a leading
day-of-month qualifier ("am 15.") blocks the month qualifier scan ("im
Juni") entirely.

See ``test/nl_corpus_en/test_nl_r152_yearly_qualifier_order.py`` for the full
defect writeup. The mechanism is shared (``_yearly_recur_qualifiers`` in
chronologia/extract/nseries.py) -- only the German day-qualifier surface ("am
<N>.") and month surface ("im <Monat>") differ, both already attested in
``test_nl_r149_adverb_recur_qualifiers.py``.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "de"

_CASES = [
    # -- the defect: order must not matter ----------------------------------
    ("jaehrlich am 15. im Juni", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=15", ""),
    ("jaehrlich im Juni am 15.", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=15", ""),
    # -- controls: month-only, no explicit day -> uniform BYMONTHDAY=1 ------
    ("jaehrlich im Juni", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    ("jedes jahr im juni", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    # -- control: bare day, no month -- must keep stranding, no invented
    # month.
    ("jaehrlich am 1.", "FREQ=YEARLY", "am 1."),
    # -- controls: pre-existing sibling readings, unaffected -----------------
    ("monatlich am 15.", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("jaehrlich", "FREQ=YEARLY", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_yearly_qualifier_folding_is_order_independent_de(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
