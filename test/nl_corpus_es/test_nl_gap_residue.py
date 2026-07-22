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
    'el día antes del examen',
])
def test_event_relative_returns_none(text):
    nomatch(text)


def test_leading_weekday_resolves_next():
    # anchored-offset: the weekday strictly after the resolved reference.
    # Pascua (next from the 2017-06-27 anchor) = Sun 2018-04-01, so the lunes
    # after it is 2018-04-02.
    s = span('el lunes después de pascua').start
    assert (s.year, s.month, s.day) == (2018, 4, 2)
