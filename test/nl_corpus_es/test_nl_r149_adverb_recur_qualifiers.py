# -*- coding: utf-8 -*-
"""R149: a bare frequency ADVERB ("mensualmente", "anualmente",
"semanalmente") strands its trailing day/month/weekday qualifier instead of
folding it onto the rule -- see
test/nl_corpus_en/test_nl_r149_adverb_recur_qualifiers.py for the full defect
writeup.  Spanish is one of the three broken siblings (English, German,
Spanish); French already folded the qualifier via a different finder family
and stays a pinned control below.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "es"

_CASES = [
    # -- monthly adverb + day-of-month qualifier ("el" is both the Spanish
    # "on" connector AND an article -- the fix reuses the exact capture the
    # "cada mes el 15" reading already uses). -------------------------------
    ("mensualmente el 15", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("mensualmente el 1", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    # -- yearly adverb + month qualifier ------------------------------------
    ("anualmente en junio", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    ("anualmente en diciembre", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=1", ""),
    # -- weekly adverb + article-led weekday plural ("los lunes" -- the
    # article "los" is not the Spanish "on" connector ("el"), so the loose
    # qualifier fallback (article-then-weekday) is what reads this). -------
    ("semanalmente los lunes", "FREQ=WEEKLY;BYDAY=MO", ""),
    # -- controls: bare adverbs, no qualifier, unchanged --------------------
    ("mensualmente", "FREQ=MONTHLY", ""),
    ("anualmente", "FREQ=YEARLY", ""),
    ("semanalmente", "FREQ=WEEKLY", ""),
    ("diariamente", "FREQ=DAILY", ""),
    # -- control: the "cada"/"todo" (every) determiner sibling reading must
    # be unchanged ------------------------------------------------------
    ("cada mes el 15", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("cada ano en junio", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_adverb_recurrence_folds_qualifier(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
