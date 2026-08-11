"""R114: "the second-to-last <weekday> of <month>" -- BYDAY=-2, never the
bare "last" reading.

Before the fix ``extract_timespan("the second-to-last friday of november")``
resolved to 27 November 2026 (the LAST Friday) with remainder "the
second-to" -- ``_recur_nth_weekday``'s sibling in the grammar-based single-
span engine (``scoped_ordinal``) only recognised the bare "last" marker
before a WEEKDAY, so the leading "second-to" qualifier was silently stripped
and stranded instead of changing the answer. Fixed by three new
``scoped_ordinal`` orders (``chronologia/extract/base_grammar.py``'s
counterpart in ``chronologia/locale/en/lang.json``'s ``base_grammar.extend``)
recognising "<ORD> to <NTOLAST>" / "<next> to <NTOLAST>" / "<PENULT>" ahead
of WEEKDAY, resolved in ``_resolve_scoped_ordinal``
(``chronologia/extract/resolver.py``).

Golds are independent calendar arithmetic: November 2026's Fridays are the
6th, 13th, 20th and 27th (verified via Python's ``calendar`` module), so
"second-to-last" is the 20th and "third-to-last" is the 13th.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

A = datetime(2026, 8, 10, 12, 0)


def _result(text, anchor=A):
    return extract_timespan(text, "en", anchor)


def _ymd(text, anchor=A):
    r = _result(text, anchor)
    if r is None:
        return None
    s = r.span.start
    return (s.year, s.month, s.day)


@pytest.mark.parametrize("text", [
    "the second-to-last friday of november",
    "the penultimate friday of november",
    "the next-to-last friday of november",
])
def test_second_to_last_friday_of_november_is_the_20th(text):
    r = _result(text)
    assert r is not None and r.remainder == ""
    assert _ymd(text) == (2026, 11, 20)


def test_third_to_last_friday_of_november_is_the_13th():
    r = _result("the third-to-last friday of november")
    assert r is not None and r.remainder == ""
    assert _ymd("the third-to-last friday of november") == (2026, 11, 13)


def test_fifth_to_last_friday_of_november_refuses():
    # out of the supported -2..-4 range -- decline rather than invent BYDAY=-5
    # or silently fall back to the "last" reading.
    assert _result("the fifth-to-last friday of november") is None


# ---------------------------------------------------------------------------
# Controls: unaffected sibling readings.
# ---------------------------------------------------------------------------
def test_last_friday_of_november_control_unchanged():
    r = _result("the last friday of november")
    assert r is not None and r.remainder == ""
    assert _ymd("the last friday of november") == (2026, 11, 27)


def test_first_friday_of_november_control_unchanged():
    r = _result("the first friday of november")
    assert r is not None and r.remainder == ""
    assert _ymd("the first friday of november") == (2026, 11, 6)
