# -*- coding: utf-8 -*-
"""R149: a bare frequency ADVERB ("monatlich", "jaehrlich", "woechentlich")
strands its trailing day/month/weekday qualifier instead of folding it onto
the rule -- see test/nl_corpus_en/test_nl_r149_adverb_recur_qualifiers.py for
the full defect writeup.  German is one of the three broken siblings (English,
German, Spanish); French already folded the qualifier via a different finder
family and stays a pinned control below.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "de"

_CASES = [
    # -- monthly adverb + day-of-month qualifier ("am" is both the German
    # "on" connector AND the qualifier marker the "jeden monat am 15."
    # reading already uses -- the fix reuses that exact capture) -----------
    ("monatlich am 15.", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("monatlich am 1.", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    # -- yearly adverb + month qualifier ------------------------------------
    ("jaehrlich im Juni", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    ("jaehrlich im Dezember", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=1", ""),
    # -- weekly adverb + bare weekday plural ("montags" fuses the habitual
    # sense into the weekday word itself, with no leading preposition or
    # article -- the loose qualifier fallback reads it directly). ----------
    ("woechentlich montags", "FREQ=WEEKLY;BYDAY=MO", ""),
    # -- controls: bare adverbs, no qualifier, unchanged --------------------
    ("monatlich", "FREQ=MONTHLY", ""),
    ("jaehrlich", "FREQ=YEARLY", ""),
    ("woechentlich", "FREQ=WEEKLY", ""),
    ("taeglich", "FREQ=DAILY", ""),
    # -- control: the "every" (jeden/jedes) determiner sibling reading must
    # be unchanged ----------------------------------------------------------
    ("jeden monat am 15.", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("jedes jahr im juni", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_adverb_recurrence_folds_qualifier(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
