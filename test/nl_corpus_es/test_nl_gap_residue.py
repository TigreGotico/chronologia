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
    'el lunes después de pascua',
    'el día antes del examen',
])
def test_event_relative_returns_none(text):
    nomatch(text)
