# -*- coding: utf-8 -*-
"""R155 (es) -- sibling of ``test_nl_r155_weekly_qualifier_order.py`` (en):
a leading clock ("a las 9") must not block the WEEKLY BYDAY qualifier scan.

Vocabulary confirmed attested in the es corpus before writing this file:
``marker_freq_weekly.voc`` ("semanalmente"), ``marker_at.voc`` ("a"/"las"),
``marker_on.voc`` ("el"), ``weekday_0.voc`` ("lunes" -- Monday).

Spanish "at" is the MULTI-token marker "a las" and the ``clock_time``
construction itself only tags from "las" onward (span excludes the leading
"a") -- this exercises :func:`_skip_clock_at`'s gap-bridging over that
leading marker token, the same gap :func:`_apply_clock` already bridges when
it extends its own consumed span backwards.

Only the WEEKLY case is mirrored here. es MONTHLY was checked live and the
leading-clock order ("mensualmente a las 9 el 15") hits a SEPARATE,
pre-existing quirk unrelated to R155: the ``clock_time`` construction's own
match greedily swallows the following "el" token, leaving nothing for the
BYMONTHDAY qualifier scan to find even after :func:`_skip_clock_at` skips
past the clock -- a tokenizer/construction-boundary defect in the timespan
engine's own grammar, out of this defect's scope, and left unfixed/unpinned
here; report only.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "es"

_CASES = [
    # -- the defect: leading clock must not drop BYDAY ----------------------
    ("semanalmente a las 9 el lunes", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    # -- control: qualifier-then-clock order, must not regress -------------
    ("semanalmente el lunes a las 9", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_weekly_qualifier_folding_is_order_independent(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
