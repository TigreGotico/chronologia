"""Every public class has a readable repr — none leaks ``<... object at 0x>``.

Walks ``chronologia.__all__``; for each exported class it asserts the class
does not inherit the default ``object.__repr__`` (which prints an unreadable
memory address).  For the value types that are cheaply constructable it also
builds a representative instance and asserts the *instance* repr is readable
and, where the type advertises it, eval-round-trips.
"""
import inspect
from datetime import timezone

import pytest

import chronologia as c
from chronologia import AstroDate, DateSpan


def _public_classes():
    return [(name, getattr(c, name)) for name in c.__all__
            if inspect.isclass(getattr(c, name))]


@pytest.mark.parametrize("name,cls", _public_classes(),
                         ids=[n for n, _ in _public_classes()])
def test_class_defines_a_repr(name, cls):
    # No public class may fall back to object.__repr__ (the '<... at 0x>' leak).
    assert cls.__repr__ is not object.__repr__, (
        f"{name} inherits the default object repr (unreadable memory address)")


# Representative instances of the constructable value types.
def _sample_instances():
    span = DateSpan(AstroDate(2020, 1, 1), AstroDate(2020, 2, 1))
    return [
        AstroDate(2024, 6, 1, 12, 30),
        AstroDate(-3760, 9, 7, tzinfo=timezone.utc),
        span,
        AstroDate(2024, 6, 1).to_calendar("hebrew"),
        c.parse_edtf("1984-06?"),
        c.parse_rrule("FREQ=WEEKLY;BYDAY=MO"),
        c.MarsDate(50000, 12, 34, 56),
        next(iter(c.PERIODS.values())),
        c.holidays_for("US", 2024)[0],
    ]


@pytest.mark.parametrize("obj", _sample_instances(),
                         ids=lambda o: type(o).__name__)
def test_instance_repr_is_readable(obj):
    r = repr(obj)
    assert "object at 0x" not in r
    assert r                                    # non-empty
    # A dataclass repr starts with the class name; that is our readability bar.
    assert type(obj).__name__ in r


def test_dataclass_repr_roundtrips_via_eval():
    # AstroDate/DateSpan reprs are valid constructor calls (eval round-trip).
    ns = {"AstroDate": AstroDate, "DateSpan": DateSpan}
    a = AstroDate(2024, 6, 1, 12, 30, 15, 42)
    assert eval(repr(a), ns) == a
    span = DateSpan(AstroDate(1, 1, 1), AstroDate(2, 1, 1), "tabulated")
    assert eval(repr(span), ns) == span
