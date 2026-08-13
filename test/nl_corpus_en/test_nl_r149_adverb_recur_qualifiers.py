"""R149: a bare frequency ADVERB ("monthly", "annually", "weekly") strands its
trailing day/month/weekday qualifier instead of folding it onto the rule.

Before the fix, the "every"-determiner readings ("every month on the 15th",
"every year in june") already folded the qualifier onto BYMONTHDAY/BYMONTH,
but the single-word adverb path (``_recur_freq_word``) matched only the bare
freq word and left everything after it in the remainder -- so "monthly on the
15th" resolved to a bare FREQ=MONTHLY with "on the 15th" stranded, silently
losing the day-of-month the user actually named.

The fix reuses the SAME qualifier-capture helpers the "every"-gated readings
use (``_weekly_byday_qualifier``, ``_monthly_bymonthday_qualifier``,
``_yearly_bymonth_qualifier`` in chronologia/extract/nseries.py), so both
paths read the identical grammar.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "en"

_CASES = [
    # -- monthly adverb + day-of-month qualifier -------------------------
    ("monthly on the 15th", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("monthly on the 1st", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    # embedded in a longer sentence -- the qualifier is still folded, only
    # the unrelated words around it are left in the remainder.
    ("please pay the rent monthly on the 15th",
     "FREQ=MONTHLY;BYMONTHDAY=15", "please pay the rent"),
    # -- yearly adverb + month qualifier ----------------------------------
    ("annually in june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    ("annually in december", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=1", ""),
    ("the audit happens annually in june",
     "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", "the audit happens"),
    # -- weekly adverb + weekday qualifier (English keeps its own dedicated
    # "on <weekday>" finder for the un-marked case -- this pins the
    # "on"-marked adverb form, which reuses the SAME qualifier helper the
    # "every 2 weeks on tuesday" reading already uses).
    # NOTE: the plural "weekly on tuesdays" is claimed by the dedicated
    # "on <weekday>" finder (_recur_on_weekdays), which runs BEFORE the
    # adverb path and already reads the weekday correctly but strands the
    # leading "weekly" -- a pre-existing, narrower defect in a DIFFERENT
    # finder, out of R149's scope (R149 is about the adverb path silently
    # dropping a qualifier, not about a redundant leading rate word).
    ("weekly on tuesday", "FREQ=WEEKLY;BYDAY=TU", ""),
    # -- controls: bare adverbs, no qualifier, must be unchanged -----------
    ("monthly", "FREQ=MONTHLY", ""),
    ("annually", "FREQ=YEARLY", ""),
    ("weekly", "FREQ=WEEKLY", ""),
    ("daily", "FREQ=DAILY", ""),
    # -- control: the "every"-determiner sibling reading must be unchanged -
    ("every month on the 15th", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("every year in june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    ("every 2 weeks on tuesday", "FREQ=WEEKLY;INTERVAL=2;BYDAY=TU", ""),
    # -- control: daily adverb + clock qualifier, a DIFFERENT finder
    # (_apply_clock, not the adverb path this fix touches) -- must still work.
    ("daily at 9am", "FREQ=DAILY;BYHOUR=9", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_adverb_recurrence_folds_qualifier(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
