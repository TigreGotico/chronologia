""""the next/last <N> quarters" / "the next/last <N> weekends" -- R75.

Two silent-wrong defects fixed here:

* "the next/last N quarters" used to bind through ``quarter_ref`` (the
  quarter-NUMBER construction, "Q<N>"), stranding the REL_MARKER in the
  remainder and reading "the next 2 quarters" as the CURRENT calendar
  quarter -- in the past relative to "next". Now a dedicated
  ``rel_span_quarter`` construction reads it calendar-aligned: "the next N
  quarters" is the next N whole calendar quarters starting at the next
  quarter boundary; "the last N quarters" is the N whole quarters already
  ended. This matches the singular "the next quarter" (``rel_period`` /
  ``quarter_ref``), which is calendar-aligned too.

* "the next/last N weekends" used to bind through ``weekend_ref`` (the bare
  weekend construction, no NUM support), stranding the count in the
  remainder and returning a single (wrong) weekend regardless of N. Now a
  dedicated ``rel_span_weekend`` construction reads it as the *covering*
  span from the start of the nearest upcoming (or, for "last", the Nth-back)
  weekend through the end of the Nth. This is deliberately asymmetric with
  the singular "next weekend" (which skips the imminent weekend): a COUNT of
  weekends naturally starts with the soonest one.

Anchor: Wednesday 2026-08-05 (Q3 2026). Golds are computed by independent
calendar arithmetic, not read back from the parser.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2026, 8, 5, 12, 0)


def _span(text):
    r = extract_timespan(text, "en", A)
    return None if r is None else (r.span.start, r.span.end)


@pytest.mark.parametrize("text,s,e", [
    # DEFECT: used to strand the marker and return the CURRENT quarter
    # (2026-04-01..2026-07-01), identical for "next" and "last".
    ("the next 2 quarters", AstroDate(2026, 10, 1), AstroDate(2027, 4, 1)),
    ("the last 2 quarters", AstroDate(2026, 1, 1), AstroDate(2026, 7, 1)),
    # a single quarter ahead/back
    ("the next 1 quarter", AstroDate(2026, 10, 1), AstroDate(2027, 1, 1)),
    ("the last 1 quarter", AstroDate(2026, 4, 1), AstroDate(2026, 7, 1)),
    # a longer run crosses a year boundary on both sides
    ("the next 4 quarters", AstroDate(2026, 10, 1), AstroDate(2027, 10, 1)),
    ("the last 4 quarters", AstroDate(2025, 7, 1), AstroDate(2026, 7, 1)),
])
def test_next_last_n_quarters_calendar_aligned(text, s, e):
    got = _span(text)
    assert got == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    # DEFECT: used to drop the count entirely and always return the single
    # NEXT weekend (2026-08-08..2026-08-10), same span for any N.
    ("the next 2 weekends", AstroDate(2026, 8, 8), AstroDate(2026, 8, 17)),
    ("the last 2 weekends", AstroDate(2026, 7, 25), AstroDate(2026, 8, 3)),
    ("the next 3 weekends", AstroDate(2026, 8, 8), AstroDate(2026, 8, 24)),
    ("the next 1 weekend", AstroDate(2026, 8, 8), AstroDate(2026, 8, 10)),
])
def test_next_last_n_weekends_covering_span(text, s, e):
    got = _span(text)
    assert got == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    # controls: singular calendar-aligned readings stay untouched.
    ("the next quarter", AstroDate(2026, 10, 1), AstroDate(2027, 1, 1)),
    ("the last quarter", AstroDate(2026, 4, 1), AstroDate(2026, 7, 1)),
    # singular "next weekend" deliberately SKIPS the imminent weekend --
    # asymmetric with the N-weekend covering span above, and unchanged here.
    ("the next weekend", AstroDate(2026, 8, 15), AstroDate(2026, 8, 17)),
    ("last weekend", AstroDate(2026, 8, 1), AstroDate(2026, 8, 3)),
])
def test_singular_quarter_weekend_unchanged(text, s, e):
    assert _span(text) == (s, e), text


def test_bare_quarter_number_unchanged():
    # "Q2 2026" and bare "2 quarters" (no REL_MARKER) still read through
    # quarter_ref -- the quarter-NUMBER construction this PR does not touch.
    assert _span("Q2 2026") == (AstroDate(2026, 4, 1), AstroDate(2026, 7, 1))
    assert _span("2 quarters") == (AstroDate(2026, 4, 1), AstroDate(2026, 7, 1))


def test_next_n_weeks_unchanged():
    # the pre-existing rel_span UNIT family (R67) is untouched by the new
    # quarter/weekend siblings.
    assert _span("the next 3 weeks") == (AstroDate(2026, 8, 5),
                                          AstroDate(2026, 8, 26))


def test_every_quarter_recurrence_unchanged():
    # "every quarter on the 15th" is a recurrence (nseries), a completely
    # separate code path from the rel_span_quarter span reading; it must not
    # regress.
    r = extract_timespan("every quarter on the 15th", "en", A)
    assert r is not None
    assert r.span.start == AstroDate(2026, 8, 15)
    assert r.remainder == "every quarter"
