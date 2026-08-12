# -*- coding: utf-8 -*-
"""R126 -- the RECURRENCE clock-range binder never learned the postposed
"between X and Y" construction PR #677 (R118) added to the single-span
engine (:func:`~chronologia.extract.timespan._extract_range`).

Hungarian frames a closed clock range with its "between" word placed AFTER
the pair ("9 és 17 óra között" == "9 and 17 hour between"), unlike English
"between A and B" which leads the pair.  Before this fix
:func:`~chronologia.extract.nseries._apply_clock_range` only recognised a
LEADING "between"/"from" marker, so a postposed clause never bound there;
it then fell through to :func:`~chronologia.extract.nseries._apply_range_bound`
(declines -- a bare-number range names no calendar date) and finally to
:func:`~chronologia.extract.nseries._apply_clock`'s generic clock-list
reader, which grounds ``BYHOUR`` off whichever clock-shaped match it meets
FIRST in the token stream -- the RIGHT endpoint ("17"), not the range's
start -- and strands the connector/marker in the remainder:
"minden nap 9 és 17 óra között" -> ``BYHOUR=17``, remainder "9 és között".

The fix mirrors #677's own convention: ``BYHOUR`` pins to the range's
left/start endpoint (the same convention "daily from 9 to 5" already uses
for the leading construction), the whole clause -- connector, both
endpoints, and the trailing marker -- is consumed, and the marker vocab
(``marker_between_post.voc``) is reused unchanged from the single-span fix.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "hu"
_A = datetime(2026, 8, 12, 12, 0)


@pytest.mark.parametrize("text,rrule,remainder", [
    # the defect as reported: postposed clock range on a daily rule.
    ("minden nap 9 és 17 óra között", "FREQ=DAILY;BYHOUR=9", ""),
    # "közt" is the short synonym marker_between_post.voc also carries.
    ("minden nap 9 és 17 óra közt", "FREQ=DAILY;BYHOUR=9", ""),
    # the left endpoint's own "óra" is optional -- only the right one needs
    # to spell it out, licensing the bare left reading (mirrors the
    # single-span "9 és 17 óra között" test in test_nl_r118_between_range.py).
    ("minden nap 9 óra és 17 óra között", "FREQ=DAILY;BYHOUR=9", ""),
    # swapped order: BYHOUR pins to whichever number comes FIRST in text,
    # not to a fixed absolute hour -- proves the fix reads the range's
    # start endpoint rather than always keeping the smaller/larger number.
    ("minden nap 17 és 9 óra között", "FREQ=DAILY;BYHOUR=17", ""),
    # weekday-scoped recurrence: the postposed range composes with an
    # explicit BYDAY base exactly like the leading construction does.
    ("minden hétfőn 9 és 17 óra között", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    # embedded in a longer sentence: only the range clause is consumed, the
    # surrounding prose is left in the remainder untouched.
    ("A megbeszélés minden hétfőn 9 és 17 óra között van.",
     "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", "A megbeszélés van"),
])
def test_postposed_between_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_A)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# -- controls: constructions this fix must NOT disturb -----------------

@pytest.mark.parametrize("text,rrule,remainder", [
    # a plain daily/weekly rule with no clock clause at all.
    ("minden nap", "FREQ=DAILY", ""),
    ("minden hétfő", "FREQ=WEEKLY;BYDAY=MO", ""),
])
def test_controls_unaffected(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_A)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_bare_es_without_kozott_stays_a_list_not_a_range():
    # no trailing "között"/"közt" -- the postposed range must not fire; two
    # bare numbers with no unit are not a clock construction at all here,
    # so the clause stays stranded in the remainder rather than being
    # mis-read as a range or a list.
    got = extract_recurrence("minden nap 9 és 17", LANG, anchor=_A)
    assert got is not None
    rec, remainder = got
    assert rec.to_string() == "FREQ=DAILY"
    assert "9" in remainder and "17" in remainder
