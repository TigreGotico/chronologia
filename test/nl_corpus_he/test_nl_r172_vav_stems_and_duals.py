# -*- coding: utf-8 -*-
"""R172: two related Hebrew gaps in the vav-conjunction / spelled-number fold
hooks (``chronologia.extract.numfold_semitic``).

1. Curated vav-strip stems (#712's ``_he_vav_strip``) omitted two everyday
   temporal-function words: לפני (before/ago, ``marker_before.voc``) and
   the bet-prefixed weekday noun ביום (``weekday_*.voc``'s curated duplicate
   surface).  A vav-prefixed sentence built on either ("ולפני יום", "וביום
   ראשון הבא") either dropped the whole mention or stranded the vav-glued
   word in the remainder, unlike every other curated stem.

2. Hebrew dual-noun unit surfaces (יומיים, שבועיים, שעתיים, ...) carry their
   own "two" meaning fused into the word -- there is no separate NUM token
   for the ``NUM UNIT`` offset pre-amble to read, so "לפני יומיים" (two days
   ago) fell to ``None`` while the analytic "לפני שני ימים" / "לפני 2 ימים"
   already worked.  Fixed by splitting each dual token into a synthetic ``2``
   NUM token followed by the ordinary plural unit word it is dual for
   (``_he_dual_split``), reusing the existing NUM+UNIT reading with no
   grammar/resolver change.

Gold spans are computed by independent :mod:`datetime` arithmetic against the
shared ANCHOR (Tuesday 2017-06-27, 13:04), converted through ``ad()``.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start, start_end


# --------------------------------------------------------------------------
# 1a. vav + לפני (before/ago) -- total drop before the fix.
# --------------------------------------------------------------------------
def test_vav_before_bare_day_ago():
    r, remainder = parse("ולפני יום")
    assert (r.start, r.end) == (ad(ANCHOR - timedelta(days=1)), ad(ANCHOR))
    assert remainder == ""


def test_vav_before_numbered_offset():
    offset_start = ANCHOR - timedelta(hours=3)
    r, remainder = parse("ולפני 3 שעות")
    assert (r.start, r.end) == (ad(offset_start),
                                 ad(offset_start + timedelta(hours=1)))
    assert remainder == ""


# --------------------------------------------------------------------------
# 1b. vav + ביום (bet-prefixed weekday noun) -- remainder stranded the vav-
# glued word before the fix ("ולפני" mention resolved, "וביום" left over).
# --------------------------------------------------------------------------
def test_vav_beyom_next_sunday_full_consumption():
    """Tuesday 2017-06-27 -> the NEXT Sunday is 2017-07-02."""
    r, remainder = parse("וביום ראשון הבא")
    assert r.start == ad(ANCHOR.replace(year=2017, month=7, day=2, hour=0,
                                        minute=0, second=0, microsecond=0))
    assert r.width == timedelta(days=1)
    assert remainder == ""


# --------------------------------------------------------------------------
# 2. Dual unit forms -- flat None before the fix.
# --------------------------------------------------------------------------
#: a relative-offset span is ``[start, start + 1*unit)`` (one unit wide) --
#: only the implicit-1 bare form happens to close exactly on the anchor, so a
#: dual (quantity 2) closes ONE unit short of the anchor, matching its
#: analytic "שני X" sibling (see ``test_control_analytic_two_days_ago``).
@pytest.mark.parametrize("text,offset,width", [
    ("לפני יומיים", timedelta(days=2), timedelta(days=1)),
    ("לפני שבועיים", timedelta(weeks=2), timedelta(weeks=1)),
    ("לפני שעתיים", timedelta(hours=2), timedelta(hours=1)),
    ("לפני דקתיים", timedelta(minutes=2), timedelta(minutes=1)),
])
def test_dual_ago(text, offset, width):
    r, remainder = parse(text)
    start_dt = ANCHOR - offset
    assert (r.start, r.end) == (ad(start_dt), ad(start_dt + width))
    assert remainder == ""


def test_dual_ago_month():
    """חודשיים (two months ago): calendar-month arithmetic, not 60 days;
    span closes one calendar month after its own start (April 27 -> May 27),
    not on the anchor."""
    r, remainder = parse("לפני חודשיים")
    assert r.start == ad(ANCHOR.replace(month=4))
    assert r.end == ad(ANCHOR.replace(month=5))
    assert remainder == ""


def test_dual_ago_year():
    """שנתיים (two years ago): calendar-year arithmetic; span closes one
    calendar year after its own start, not on the anchor."""
    r, remainder = parse("לפני שנתיים")
    assert r.start == ad(ANCHOR.replace(year=2015))
    assert r.end == ad(ANCHOR.replace(year=2016))
    assert remainder == ""


def test_dual_ago_vav_prefixed():
    """The dual split composes with the vav strip: a vav-prefixed marker
    ahead of a bare dual unit ("ולפני יומיים") must resolve exactly like its
    non-vav sibling."""
    r, remainder = parse("ולפני יומיים")
    start_dt = ANCHOR - timedelta(days=2)
    assert (r.start, r.end) == (ad(start_dt), ad(start_dt + timedelta(days=1)))
    assert remainder == ""


# --------------------------------------------------------------------------
# Controls: nothing the fix touches must regress.
# --------------------------------------------------------------------------
def test_control_bare_hour_ago_unaffected():
    assert start_end("לפני שעה") == (ad(ANCHOR - timedelta(hours=1)),
                                       ad(ANCHOR))


def test_control_bare_day_and_week_ago_unaffected():
    assert start("לפני יום") == ad(ANCHOR - timedelta(days=1))
    assert start("לפני שבוע") == ad(ANCHOR - timedelta(weeks=1))


def test_control_analytic_two_days_ago_unaffected():
    """The two pre-existing analytic routes to "two days ago" must still
    both work and agree with the new dual reading."""
    start_dt = ANCHOR - timedelta(days=2)
    expect = (ad(start_dt), ad(start_dt + timedelta(days=1)))
    assert start_end("לפני שני ימים") == expect
    assert start_end("לפני 2 ימים") == expect


def test_control_non_vav_beyom_next_sunday_unaffected():
    r, remainder = parse("ביום ראשון הבא")
    assert r.start == ad(ANCHOR.replace(year=2017, month=7, day=2, hour=0,
                                        minute=0, second=0, microsecond=0))
    assert remainder == ""


def test_control_r160_vav_named_day_unaffected():
    """Neighbouring #712 stems (unrelated to לפני/ביום) must be untouched --
    a named day floors to midnight, unlike the exact-instant offset above."""
    from ._corpus import AstroDate
    assert start("ומחר") == AstroDate(2017, 6, 28)
