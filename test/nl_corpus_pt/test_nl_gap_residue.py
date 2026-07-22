"""Wave 3 -- residue that must return None cleanly.

Event-relative references ("the Monday after Easter", "the day before
the deadline") name a day only reachable through an event registry or
dialogue context the engine deliberately does not carry, and compound
offsets ("the week after next", "a week on Tuesday") the grammar does
not spell.  The contract: no fabricated date from an anchor it cannot
resolve -- these return None, never a wrong span.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, nomatch, span


@pytest.mark.parametrize("text", [
    'o dia antes do exame',
])
def test_event_relative_returns_none(text):
    nomatch(text)


def test_leading_weekday_resolves_next():
    # the leading bare weekday resolves to its next occurrence; the event
    # residue ("depois da páscoa") the engine does not carry
    ahead = (0 - ANCHOR.weekday()) % 7 or 7          # 0 == Monday (segunda)
    exp = (ANCHOR + timedelta(days=ahead)).date()
    s = span('a segunda depois da páscoa').start
    assert (s.year, s.month, s.day) == (exp.year, exp.month, exp.day)
