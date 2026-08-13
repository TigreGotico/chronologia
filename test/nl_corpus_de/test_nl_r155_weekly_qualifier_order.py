# -*- coding: utf-8 -*-
"""R155 (de) -- sibling of ``test_nl_r155_weekly_qualifier_order.py`` (en):
a leading clock ("um 9") must not block the WEEKLY BYDAY qualifier scan.

Vocabulary confirmed attested in the de corpus before writing this file:
``marker_freq_weekly.voc`` ("woechentlich"/"wöchentlich"), ``marker_at.voc``
("um"), ``marker_on.voc`` ("am"), ``weekday_1.voc`` ("montag" -- Monday).
Only the WEEKLY case is mirrored here; the MONTHLY/YEARLY siblings are left
to the en file -- de's own qualifier-order behaviour for those was checked
live and already works in both orders, so no further defect surface needed
pinning per-locale.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "de"

_CASES = [
    # -- the defect: leading clock must not drop BYDAY ----------------------
    ("wöchentlich um 9 am montag", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    # -- control: qualifier-then-clock order, must not regress -------------
    ("wöchentlich am montag um 9", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_weekly_qualifier_folding_is_order_independent(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
