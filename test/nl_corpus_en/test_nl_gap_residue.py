"""Wave 3 -- residue that must return None cleanly.

Event-relative references ("the Monday after Easter", "the day before
the deadline") name a day only reachable through an event registry or
dialogue context the engine deliberately does not carry, and compound
offsets ("the week after next", "a week on Tuesday") the grammar does
not spell.  The contract: no fabricated date from an anchor it cannot
resolve -- these return None, never a wrong span.
"""
import pytest

from ._corpus import nomatch


@pytest.mark.parametrize("text", [
    'the monday after easter',
    'the day before the deadline',
    'the day after the wedding',
    'the friday before the exam',
    'a couple of fridays from now',
    'the week after next',
    'the tuesday before the meeting',
    'a week on tuesday',
])
def test_event_relative_returns_none(text):
    nomatch(text)
