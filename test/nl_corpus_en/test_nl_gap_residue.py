"""Wave 3 -- residue that must return None cleanly.

Event-relative references anchored on a *non-weekday* noun ("the day
before the deadline") name a day only reachable through an event registry
or dialogue context the engine deliberately does not carry, and compound
offsets the grammar does not spell ("the week after next").  The contract:
no fabricated date from an anchor it cannot resolve -- these return None,
never a wrong span.

A phrase that *opens* with a bare weekday is different: the weekday itself
is a valid reference (its next strictly-future occurrence), so the engine
resolves that leading day and reports the rest as residue.  Those cases are
asserted positively below, not as non-matches.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, nomatch, span


@pytest.mark.parametrize("text", [
    'the day before the deadline',
    'the day after the wedding',
    'a couple of fridays from now',
    'the week after next',
])
def test_event_relative_returns_none(text):
    nomatch(text)


@pytest.mark.parametrize("text,idx", [
    ('the monday after easter', 0),
    ('the friday before the exam', 4),
    ('the tuesday before the meeting', 1),
    ('a week on tuesday', 1),
])
def test_leading_weekday_resolves_next(text, idx):
    # the leading bare weekday resolves to its next occurrence; the rest of
    # the phrase is unsupported residue the engine does not fold in
    ahead = (idx - ANCHOR.weekday()) % 7 or 7
    exp = (ANCHOR + timedelta(days=ahead)).date()
    s = span(text).start
    assert (s.year, s.month, s.day) == (exp.year, exp.month, exp.day)
