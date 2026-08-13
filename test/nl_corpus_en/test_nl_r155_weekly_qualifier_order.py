# -*- coding: utf-8 -*-
"""R155 (en) -- WEEKLY qualifier folding is ORDER-SENSITIVE (unfixed sibling
of R152, which fixed the very same asymmetry for the YEARLY adverb path):
a leading clock ("at 9") blocks the BYDAY qualifier scan entirely.

``_recur_freq_word``'s qualifier scan only ever looked for its qualifier
(``_weekly_byday_qualifier_loose`` for WEEKLY, ``_monthly_bymonthday_qualifier``
for MONTHLY, ``_yearly_recur_qualifiers`` for YEARLY) immediately after the
freq adverb. "weekly **at 9** on monday" put the clock right where the BYDAY
scan looked, so the scan found nothing there and gave up -- ``_apply_clock``
(run later, over the whole token stream) still found and folded the "at 9"
independently, but "on monday" was left wholly unclaimed by anything and
stranded verbatim in the remainder, with BYDAY silently empty. "weekly on
monday at 9am" (the qualifier first, clock second) hit the scan's expected
position directly and folded correctly -- an asymmetry that must not exist
for two spellings of the same rule.

Fixed by :func:`_skip_clock_at`, shared by the WEEKLY/MONTHLY/YEARLY
branches: when the immediate-position qualifier scan finds nothing, it
checks whether a clock construction sits there instead, and if so retries
the qualifier scan just past it -- WITHOUT claiming the clock's own tokens,
so :func:`_apply_clock`'s independent unconsumed-token scan still resolves
and folds the hour exactly as it always did. DAILY carries no further
qualifier of its own ("daily at 9" already worked, pinned below as an
unaffected control) so it needed no analogous fix.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "en"

_CASES = [
    # -- the defect: WEEKLY, leading clock must not drop BYDAY -------------
    ("weekly at 9 on monday", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    ("weekly at 9:30 on friday", "FREQ=WEEKLY;BYDAY=FR;BYHOUR=9;BYMINUTE=30", ""),
    # -- control: WEEKLY, qualifier-then-clock order, must not regress -----
    ("weekly on monday at 9am", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    # -- same mechanism, MONTHLY sibling -------------------------------
    ("monthly at 9 on the 15th", "FREQ=MONTHLY;BYMONTHDAY=15;BYHOUR=9", ""),
    ("monthly on the 15th at 9am", "FREQ=MONTHLY;BYMONTHDAY=15;BYHOUR=9", ""),
    # -- same mechanism, YEARLY sibling (R152 already fixed month<->day
    # order; this pins that a leading clock doesn't reintroduce the bug) --
    ("yearly at 9 in june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1;BYHOUR=9", ""),
    ("yearly in june at 9", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1;BYHOUR=9", ""),
    # -- control: DAILY has no further qualifier, unaffected by the defect
    # or the fix ------------------------------------------------------------
    ("daily at 9", "FREQ=DAILY;BYHOUR=9", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_weekly_qualifier_folding_is_order_independent(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
