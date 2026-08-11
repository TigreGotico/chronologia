"""Compound duration folding across two shapes ``apply_compound_offset``
(``chronologia/extract/anchored.py``) previously missed -- defect R109.

* A POSTPOSED direction marker ("3 months and 2 days **ago**") closes the
  phrase instead of opening it, so the LEADING ``NUM UNIT [and|,]`` chunk
  sat before the matched ``NUM UNIT MARKER`` span and the forward-only scan
  never saw it -- only the trailing "2 days ago" applied, stranding "3
  months and" in the remainder.  Folding now scans backward too, so both
  textual orderings ("3 months and 2 days ago" / "2 days and 3 months ago")
  land on the identical instant, mirroring the forward compound's own
  order-independence guarantee (see ``test_nl_compound_mixed_durations.py``).

* ``rel_span`` ("the next/last N units") is a different construction from
  ``relative_offset`` entirely, so the compound pass skipped it outright: a
  trailing chunk ("the next 2 weeks **and 3 days**") was simply stranded in
  the remainder instead of extending the rolling span's far end.

Every expected value is hand-derived with ``dateutil.relativedelta``/
``timedelta`` arithmetic that never reads the parser's own output back as
gold.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, ad, parse, start_end

LANG = "en"


def _point(anchor=ANCHOR, **delta):
    dt = anchor + relativedelta(**delta)
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


# -- postposed "ago" compounds: leading chunk must fold, both orderings ----

@pytest.mark.parametrize("text", [
    "3 months and 2 days ago",
    "2 days and 3 months ago",          # reversed textual order: same instant
])
def test_ago_compound_folds_leading_chunk(text):
    span_, remainder = parse(text)
    exp_start = _point(months=-3, days=-2)
    assert span_.start == exp_start, f"{text!r}: {span_.start} != {exp_start}"
    assert span_.end == exp_start + timedelta(days=1), \
        "finest unit here is 'day' -> a day-wide span"
    assert remainder == "", f"{text!r} left a remainder: {remainder!r}"


def test_ago_compound_three_part():
    span_, remainder = parse("1 year, 2 months and 3 days ago")
    exp_start = _point(years=-1, months=-2, days=-3)
    assert span_.start == exp_start
    assert span_.end == exp_start + timedelta(days=1)
    assert remainder == ""


def test_ago_compound_calendar_then_fixed_order():
    # "3 months and 2 hours ago": calendar chunk first, fixed chunk second,
    # same convention as the forward "in 3 months and 2 hours" compound.
    span_, remainder = parse("3 months and 2 hours ago")
    exp_start = _point(months=-3, hours=-2)
    assert span_.start == exp_start
    assert span_.end == exp_start + timedelta(hours=1)
    assert remainder == ""


# -- rel_span: trailing chunk must extend the rolling span -----------------

def test_rel_span_next_extends_forward():
    start, end = start_end("the next 2 weeks and 3 days")
    assert start == ad(ANCHOR.replace(hour=0, minute=0, second=0,
                                      microsecond=0))
    assert end == ad(ANCHOR.replace(hour=0, minute=0, second=0,
                                    microsecond=0)
                     + timedelta(weeks=2, days=3))


def test_rel_span_last_extends_backward():
    start, end = start_end("the last 2 weeks and 3 days")
    today = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    assert end == ad(today)
    assert start == ad(today - timedelta(weeks=2, days=3))


def test_rel_span_extends_with_remainder_consumed():
    span_, remainder = parse("the next 2 weeks and 3 days")
    assert remainder == ""


# -- controls: unchanged behavior must stay pinned --------------------------

def test_ago_bare_control_unchanged():
    span_, remainder = parse("3 months ago")
    exp_start = _point(months=-3)
    assert span_.start == exp_start
    assert span_.end == _point(months=-2)
    assert remainder == ""


def test_rel_span_bare_control_unchanged():
    start, end = start_end("the next 2 weeks")
    today = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    assert start == ad(today)
    assert end == ad(today + timedelta(weeks=2))


def test_forward_compound_still_unchanged():
    # the forward-marker compound (fixed in PR #666) must be untouched by
    # this change.
    start, end = start_end("in 3 months and 2 days")
    exp_start = _point(months=3, days=2)
    assert start == exp_start
    assert end == exp_start + timedelta(days=1)


def test_rel_period_next_and_trailing_chunk_pinned():
    # probed convention: "next week and 2 days" is a ``rel_period`` (a
    # calendar-aligned whole week), not a ``rel_span`` -- this fix does not
    # extend it, so the trailing chunk still strands in the remainder. Pinned
    # here as the CURRENT, deliberately out-of-scope behavior (see R109
    # task notes), not asserted as correct.
    span_, remainder = parse("next week and 2 days")
    assert remainder == "and 2 days"
