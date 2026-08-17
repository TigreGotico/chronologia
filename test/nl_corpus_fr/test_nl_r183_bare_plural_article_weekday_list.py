# -*- coding: utf-8 -*-
"""fr bare PLURAL definite article + weekday(s) -- habitual recurrence.

"les lundis" ("on Mondays") reads exactly like "tous les lundis" -- the
plural article alone marks the habitual sense, mirroring pt's "às
segundas-feiras" and es's "los lunes". French restates the article before
each list item ("les lundis ET LES mercredis"), unlike Spanish, so the
weekday collector must swallow the repeated article rather than stranding
the second weekday. "le lundi" (singular article) is ambiguous between "next
Monday" and a habitual reading and is deliberately never read as a
recurrence here.
"""
import pytest
from datetime import datetime

from chronologia.extract import extract_recurrence, extract_timespans

LANG = "fr"
_ANCHOR = datetime(2026, 8, 14, 10, 0)

_CASES = [
    ("les lundis et les mercredis", "FREQ=WEEKLY;BYDAY=MO,WE", ""),
    ("les mardis et les jeudis", "FREQ=WEEKLY;BYDAY=TU,TH", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bare_plural_article_weekday_list(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# working control -- the explicit "tous les" quantifier must keep reading
# exactly as before the bare-article idiom was added.
def test_tous_les_control_unchanged():
    got = extract_recurrence("tous les lundis et mercredis", LANG, anchor=_ANCHOR)
    assert got is not None
    assert got[0].to_string() == "FREQ=WEEKLY;BYDAY=MO,WE"
    assert got[1] == ""


# adversarial: the SINGULAR article names one upcoming date, or is at best
# ambiguous -- "le lundi" must not regress into a recurrence just because
# the plural sibling now reads as one.
@pytest.mark.parametrize("text", ["le lundi", "le mercredi"])
def test_singular_article_weekday_is_not_a_recurrence(text):
    assert extract_recurrence(text, LANG, anchor=_ANCHOR) is None


# the timespan path (a single upcoming date) must be unaffected by the new
# recurrence reading -- "le lundi" still resolves to the next Monday.
def test_singular_article_weekday_timespan_unaffected():
    ts = extract_timespans("le lundi", LANG, anchor=_ANCHOR)
    assert len(ts) == 1
    assert ts[0].span.start.day == 17 and ts[0].span.start.month == 8
