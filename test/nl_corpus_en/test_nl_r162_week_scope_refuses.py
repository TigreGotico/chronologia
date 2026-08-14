# -*- coding: utf-8 -*-
"""R162 (en) -- an ordinal-weekday recurrence with a WEEK-scoped tail ("of
next week" / "of last week" / "of the week" / "of this week") must refuse
the whole extraction, not silently ship a WRONG unbounded rule.

``_recur_nth_weekday``'s "... of [every] (month|year)" bounded-scope guard
(R153/#709) only ever recognised the ``month``/``year`` unit nouns after a
non-zero deixis token ("next"/"last") -- the ``week`` unit noun matched
neither that guard nor the month/year fold branches below it, so the whole
match fell through unclaimed for ANY "of ... week" tail (bounded or not). A
weaker downstream finder (``_recur_every``'s ordinal-weekday ellipsis) then
re-read only the ordinal-weekday head ("every 3rd tuesday") as a bare
``FREQ=WEEKLY;INTERVAL=3;BYDAY=TU`` rule, stranding "of next week" (or "of
last week"/"of the week"/"of this week") as remainder -- silently wrong,
because the folded rule already IS a 3-week cadence and the stranded tail
claimed something else entirely.

DECIDED SEMANTICS: unlike month/year (R145/R151/R153, which fold the
zero-offset/bare case and only refuse the non-zero-deixis one), a week-scoped
tail has NO fold branch at all, refused/deixis alike: a week has exactly one
of any given weekday, so "every 3rd tuesday of the week" is degenerate ("the
week" cannot contain a 3rd tuesday), and "of next/last week" is a single
bounded week, not an unbounded RFC 5545 recurrence -- exactly the shape R153
already refuses for month/year's non-zero-deixis case. This test extends
that refusal to ALL "of ... week" scopes, deixis included.

de/es siblings: R153 (the month/year sibling this defect mirrors) shipped
en-only with no de/es corpus file at all, and the ``week`` unit surfaces that
exist in de (``woche``/``wochen``) and es (``semana``/``semanas``) sit behind
the exact same "of [deixis] <unit>" tail grammar R153 never got a de/es
sibling for -- so this defect is treated as unattested there too and stays
en-only, consistent with R153's precedent.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "en"

_REFUSE_CASES = [
    "every 3rd tuesday of next week",
    "every 3rd tuesday of last week",
    "every 3rd tuesday of the week",
    "every 3rd tuesday of this week",
    "every last monday of next week",
    "every last monday of last week",
    "every last monday of the week",
]

_CONTROL_CASES = [
    # -- controls: the week-scope refusal must not touch the already-correct
    # month/year readings (R145/R151/R153/#709) --------------------------
    ("of next month refuses", "every 3rd tuesday of next month", None, None),
    ("of next year refuses", "every 3rd tuesday of next year", None, None),
    ("of the year folds", "every 3rd tuesday of the year",
     "FREQ=YEARLY;BYDAY=3TU", ""),
    ("of this month folds", "every 3rd tuesday of this month",
     "FREQ=MONTHLY;BYDAY=3TU", ""),
    ("bare", "every 3rd tuesday", "FREQ=WEEKLY;INTERVAL=3;BYDAY=TU", ""),
]


@pytest.mark.parametrize("text", _REFUSE_CASES)
def test_week_scope_refuses_the_whole_extraction(text):
    got = extract_recurrence(text, LANG)
    assert got is None, (
        f"{text!r} named a single week but extracted {got!r} instead of "
        "refusing outright")


@pytest.mark.parametrize("label,text,rrule,remainder", _CONTROL_CASES)
def test_month_year_scope_controls_unaffected(label, text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    if rrule is None:
        assert got is None, f"{text!r} ({label}) should refuse but got {got!r}"
        return
    assert got is not None, f"{text!r} ({label}) did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
