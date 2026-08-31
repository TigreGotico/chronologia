"""R114b: the UNSCOPED "the second-to-last <weekday>" (no "of <month/year>")
-- anchor-relative, one whole week earlier than the bare "last" reading,
never the bare "last" answer itself.

Before the fix ``extract_timespan("the second-to-last friday")`` resolved to
the SAME date as ``extract_timespan("the last friday")`` -- ``weekday_ref``
had no order at all for a "second-to-last"/"penultimate"/"next-to-last"
qualifier ahead of a bare WEEKDAY (only the scoped "... of <month/year>"
sibling in ``scoped_ordinal`` recognised it), so the qualifier was silently
stranded in the remainder and the plain "last" answer returned -- a
one-week-off, silently wrong span. Fixed by three new ``weekday_ref`` orders
(``chronologia/locale/en/lang.json``'s ``base_grammar.extend``) mirroring
``scoped_ordinal``'s existing "<ORD> to <NTOLAST>" / "<next> to <NTOLAST>" /
"<PENULT>" prefixes, resolved in ``_resolve_weekday_ref``
(``chronologia/extract/resolver.py``) by reusing the SAME -N-from-last
arithmetic ``_resolve_scoped_ordinal`` already applies, anchored on the
current week instead of a named scope.

Golds are independent calendar arithmetic (verified via Python's
``calendar`` module), never read back from the parser.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

A = datetime(2026, 6, 15, 12, 0)  # a Monday; the anchor's own week's Friday
                                   # has not happened yet, so "last friday"
                                   # is the most recent PAST Friday.


def _result(text, anchor=A):
    return extract_timespan(text, "en", anchor)


def _ymd(text, anchor=A):
    r = _result(text, anchor)
    if r is None:
        return None
    s = r.span.start
    return (s.year, s.month, s.day)


@pytest.mark.parametrize("text", [
    "the second-to-last friday",
    "the penultimate friday",
    "the next-to-last friday",
])
def test_second_to_last_friday_is_one_week_before_last(text):
    r = _result(text)
    assert r is not None and r.remainder == ""
    # last friday relative to 2026-06-15 is 2026-06-12; second-to-last is
    # exactly one calendar week earlier.
    assert _ymd(text) == (2026, 6, 5)


def test_third_to_last_friday_is_two_weeks_before_last():
    r = _result("the third-to-last friday")
    assert r is not None and r.remainder == ""
    assert _ymd("the third-to-last friday") == (2026, 5, 29)


def test_fifth_to_last_friday_refuses():
    # out of the supported -2..-4 range -- decline rather than invent BYDAY=-5
    # or silently fall back to the "last" reading.
    assert _result("the fifth-to-last friday") is None


def test_last_friday_control_unchanged():
    r = _result("the last friday")
    assert r is not None and r.remainder == "the"
    assert _ymd("the last friday") == (2026, 6, 12)


def test_second_to_last_friday_crosses_month_boundary():
    # anchor is itself a Friday: 2026-07-03. "last friday" is the anchor's
    # own weekday reading STRICTLY PAST, 2026-06-26 (one week back); the
    # "second-to-last" (adversarial: crosses from July into June) is a
    # further week back, 2026-06-19.
    anchor = datetime(2026, 7, 3, 12, 0)
    r = _result("the second-to-last friday", anchor)
    assert r is not None and r.remainder == ""
    assert _ymd("the second-to-last friday", anchor) == (2026, 6, 19)
    assert _ymd("the last friday", anchor) == (2026, 6, 26)


# ---------------------------------------------------------------------------
# Year-scoped "... of <GYEAR>" -- an explicit numeric-year scope must win
# over the unscoped anchor-relative reading, and give a DIFFERENT answer
# than the bare (no "of <year>") phrase.
#
# Before this pin, ``scoped_ordinal`` had no bare-GYEAR order for the
# NTOLAST/PENULT prefixes (only "... of MONTH ..." and "... of
# REL_MARKER? SCOPE_UNIT"), so the new unscoped ``weekday_ref`` orders this
# module pins outranked the scoped reading entirely: "the second-to-last
# friday of 2026" resolved to 2026-06-05 (the ANCHOR-relative reading) with
# "of 2026" stranded in the remainder -- a silently wrong answer, worse
# than dev's pre-existing one-week-off defect, because the explicit year was
# discarded rather than merely mis-offset. Fixed by three matching bare-GYEAR
# ``scoped_ordinal`` orders in ``chronologia/locale/en/lang.json``, resolved
# by the SAME already-working ``gyear_tok is not None`` branch in
# ``_resolve_scoped_ordinal`` (``chronologia/extract/resolver.py``) the
# "last friday of 2026" control below already exercised -- no resolver
# change was needed.
#
# Golds: December 2026's Fridays are the 4th, 11th, 18th and 25th (verified
# via Python's ``calendar`` module).
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "the second-to-last friday of 2026",
    "the penultimate friday of 2026",
    "the next-to-last friday of 2026",
])
def test_second_to_last_friday_of_2026_is_the_18th(text):
    r = _result(text)
    assert r is not None and r.remainder == ""
    assert _ymd(text) == (2026, 12, 18)


def test_third_to_last_friday_of_2026_is_the_11th():
    r = _result("the third-to-last friday of 2026")
    assert r is not None and r.remainder == ""
    assert _ymd("the third-to-last friday of 2026") == (2026, 12, 11)


def test_fifth_to_last_friday_of_2026_refuses():
    assert _result("the fifth-to-last friday of 2026") is None


def test_last_friday_of_2026_control_unchanged():
    r = _result("the last friday of 2026")
    assert r is not None and r.remainder == ""
    assert _ymd("the last friday of 2026") == (2026, 12, 25)


def test_second_to_last_friday_with_and_without_year_differ():
    # the adversarial pair: identical phrase, only the explicit "of 2026"
    # scope differs -- the two MUST resolve to different dates. The bare
    # form is anchor-relative (2026-06-05, one week before the anchor's own
    # "last friday" of 2026-06-12); the year-scoped form names the whole of
    # 2026, landing in December.
    bare = _ymd("the second-to-last friday")
    scoped = _ymd("the second-to-last friday of 2026")
    assert bare == (2026, 6, 5)
    assert scoped == (2026, 12, 18)
    assert bare != scoped
