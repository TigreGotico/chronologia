# -*- coding: utf-8 -*-
"""R153 (en) -- an ordinal-weekday recurrence with a BOUNDED scope tail ("of
next year" / "of last year" / "of next month" / "of last month") must refuse
the whole extraction, not silently ship a WRONG unbounded rule.

``_recur_nth_weekday``'s "... of [every] (month|year)" tail (R145/#702, then
R151/#708 for the zero-offset "this") only ever consumed articles/"every"/
zero-offset deixis between "of" and the unit noun. A NON-zero deixis token
("next"/"last") sitting there matched none of the tail's branches (not
``ctx.months``, not units-is-"month", not units-is-"year") and the whole
match fell through unclaimed -- exactly the same shape of bug R145/R151 fixed
for the zero-offset and bare cases. A weaker downstream finder
(``_recur_every``'s ordinal-weekday ellipsis) then re-read only "every 3rd
tuesday" as a bare WEEKLY;INTERVAL=3 rule, stranding "of next year" as
remainder -- silently 2x-frequency-wrong (a single bounded year is not an
unbounded interval-3 weekly recurrence).

DECIDED SEMANTICS: a bounded period ("of next/last <year|month>") is not
expressible as an unbounded RFC 5545 recurrence at all, so the fix is to
REFUSE the whole extraction (``extract_recurrence`` returns ``None``) rather
than degrade to a wrong rule or strand a partial one.

"of the current year" is checked as a would-be control: the en
``marker_this``/REL_MARKER vocabulary (``chronologia/locale/en/marker_this.voc``,
value 0) has NO "current" surface, so "of the current year" is NOT the
zero-offset "this" reading and is left correctly stranding by the SAME
mechanism the "next"/"last" case above hits: "current" is not a ``REL_MARKER``
word at all, so the tail's while-loop (which only walks over ``ctx.every``/
``ctx.articles``/zero-offset ``rel_markers``) does not consume it either, and
the phrase falls through to the same weaker WEEKLY;INTERVAL=3 finder that a
genuine "next"/"last" case would have -- this is pinned as a KNOWN GAP, not a
regression: teaching the en vocabulary "current" -> REL_MARKER=0 is future
scope, tracked separately, not part of this fix.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "en"

_REFUSE_CASES = [
    "every 3rd tuesday of next year",
    "every 3rd tuesday of last year",
    "every 3rd tuesday of next month",
    "every 3rd tuesday of last month",
    "every last monday of next year",
    "every last monday of last year",
]

_CONTROL_CASES = [
    # -- controls: bounded-year fix must not touch the already-correct
    # unbounded readings (R145/#702, R151/#708) --------------------------
    ("of the year", "every 3rd tuesday of the year",
     "FREQ=YEARLY;BYDAY=3TU", ""),
    ("of this year", "every 3rd tuesday of this year",
     "FREQ=YEARLY;BYDAY=3TU", ""),
    ("of the month", "every 3rd tuesday of the month",
     "FREQ=MONTHLY;BYDAY=3TU", ""),
    ("of this month", "every 3rd tuesday of this month",
     "FREQ=MONTHLY;BYDAY=3TU", ""),
    # -- control: bare ordinal-weekday established base reading, untouched
    ("bare", "every 3rd tuesday", "FREQ=WEEKLY;INTERVAL=3;BYDAY=TU", ""),
]


@pytest.mark.parametrize("text", _REFUSE_CASES)
def test_bounded_scope_refuses_the_whole_extraction(text):
    got = extract_recurrence(text, LANG)
    assert got is None, (
        f"{text!r} named a bounded single period but extracted {got!r} "
        "instead of refusing outright")


@pytest.mark.parametrize("label,text,rrule,remainder", _CONTROL_CASES)
def test_unbounded_scope_controls_unaffected(label, text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} ({label}) did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_of_the_current_year_is_a_known_stranding_gap():
    # "current" is unattested in the en REL_MARKER vocabulary (only "this"
    # carries value 0) -- this pins the known gap rather than silently
    # letting a future vocabulary change flip this test's meaning unnoticed.
    got = extract_recurrence("every 3rd tuesday of the current year", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=WEEKLY;INTERVAL=3;BYDAY=TU"
    assert got[1] == "of the current year"
