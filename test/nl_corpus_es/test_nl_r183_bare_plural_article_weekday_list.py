# -*- coding: utf-8 -*-
"""es bare PLURAL definite article + weekday(s) -- habitual recurrence.

"los lunes" ("on Mondays") reads exactly like "todos los lunes" -- the
plural article alone marks the habitual sense, mirroring pt's "às
segundas-feiras". Spanish weekday nouns are number-invariant ("lunes" is
both singular and plural), so it is the ARTICLE's number, not the noun's,
that disambiguates: "el lunes" (singular article) names the single next
Monday and must never become a recurrence.
"""
import pytest
from datetime import datetime

from chronologia.extract import extract_recurrence, extract_timespans

LANG = "es"
_ANCHOR = datetime(2026, 8, 14, 10, 0)

_CASES = [
    ("los lunes y miércoles", "FREQ=WEEKLY;BYDAY=MO,WE", ""),
    ("los lunes y los jueves", "FREQ=WEEKLY;BYDAY=MO,TH", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bare_plural_article_weekday_list(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# working controls -- the explicit "todos los" quantifier must keep reading
# exactly as before the bare-article idiom was added.
@pytest.mark.parametrize("text,rrule", [
    ("todos los lunes y miércoles", "FREQ=WEEKLY;BYDAY=MO,WE"),
])
def test_todos_los_control_unchanged(text, rrule):
    got = extract_recurrence(text, LANG, anchor=_ANCHOR)
    assert got is not None
    assert got[0].to_string() == rrule
    assert got[1] == ""


# adversarial: a SINGULAR article names one upcoming date, never a rule --
# "el lunes" must not regress into a recurrence just because the plural
# sibling now reads as one.
@pytest.mark.parametrize("text", ["el lunes", "el miércoles"])
def test_singular_article_weekday_is_not_a_recurrence(text):
    assert extract_recurrence(text, LANG, anchor=_ANCHOR) is None


# the timespan path (a single upcoming date) must be unaffected by the new
# recurrence reading -- "el lunes" still resolves to the next Monday.
def test_singular_article_weekday_timespan_unaffected():
    ts = extract_timespans("el lunes", LANG, anchor=_ANCHOR)
    assert len(ts) == 1
    assert ts[0].span.start.day == 17 and ts[0].span.start.month == 8


def test_plural_list_timespan_path_still_reads_bare_dates():
    """The recurrence reading and the timespan reading are independent
    passes over the same text; the bare weekday list still resolves each
    weekday to its own upcoming date under extract_timespans."""
    ts = extract_timespans("los lunes y miércoles", LANG, anchor=_ANCHOR)
    assert len(ts) == 2
