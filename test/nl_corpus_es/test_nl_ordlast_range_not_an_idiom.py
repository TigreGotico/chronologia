"""Tripwire: Spanish pairs an ordlast word with its ordinary range connector,
and that must stay a range.

The engine's "<ordinal> to last" guard (``_ntolast_interior`` in
``chronologia/extract/timespan.py``) stops the range detector splitting
English "second-to-last" at its own "to". Spanish "del 2 al último día de
junio" has the same token shape -- ordinal, ``to`` connector, ordlast word --
but no such idiom, so the guard must not fire here. It is gated on the locale
declaring ``ntolast_next``, which Spanish does not.

The spans pinned below are what the engine returns; the point of the pin is
that the guard leaves them alone, not that they are the last word on how this
phrase should read.
"""
from datetime import datetime

from chronologia import extract_timespan

A = datetime(2026, 6, 15, 12, 0)


def _span(text):
    r = extract_timespan(text, "es", A)
    s, e = r.span.start, r.span.end
    return ((s.year, s.month, s.day), (e.year, e.month, e.day), r.remainder)


def test_scoped_ordlast_range_unchanged():
    assert _span("del 2 al último día de junio") \
        == ((2026, 6, 30), (2026, 7, 1), "del 2 al")


def test_unscoped_ordlast_range_unchanged():
    assert _span("del 2 al último día") \
        == ((2026, 6, 14), (2026, 6, 15), "del 2 al")
