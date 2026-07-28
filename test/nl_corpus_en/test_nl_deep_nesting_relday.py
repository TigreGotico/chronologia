"""Deep / compound relative-day nesting, hand-derived against the
Tuesday 2017-06-27 13:04 anchor.

Two silent-wrong families are pinned here:

* **"the <weekday> after next"** -- the skip-one "after next" family
  (#303/#307: day / morning / weekend after next), extended to the WEEKDAY
  unit.  Formerly the bare matcher read the weekday as its own next
  occurrence and stranded "the after next", so "the Saturday after next"
  gave *next* Saturday (06-30... 07-01) instead of the one a week past it.
  It now resolves to next-<weekday> + 7 days, consuming the whole phrase.

* **"the day after the day after tomorrow"** -- the outer "the day
  after/before" now composes onto the inner named-day idiom's resolved
  date instead of stranding, so the DOUBLE nest steps one more whole day
  past the inner result.  The offset pass iterates to a fixpoint, so
  triple+ nesting ("the day after the day after the day after tomorrow")
  composes every outer layer instead of stranding.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, span, start

_MID = ANCHOR.replace(hour=0, minute=0)


def _rem(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    return r[1]


# -- "the <weekday> after next": next occurrence + one week ---------------

@pytest.mark.parametrize("text,expected", [
    # next Saturday is 07-01; the Saturday after next is 07-08
    ("the Saturday after next", _MID + timedelta(days=11)),   # 2017-07-08
    ("Saturday after next", _MID + timedelta(days=11)),
    # next Friday is 06-30; after next is 07-07
    ("the Friday after next", _MID + timedelta(days=10)),     # 2017-07-07
    # next Monday is 07-03; after next is 07-10
    ("the Monday after next", _MID + timedelta(days=13)),     # 2017-07-10
    # next Tuesday is 07-04 (strictly future from the Tuesday anchor); +7 = 07-11
    ("the Tuesday after next", _MID + timedelta(days=14)),    # 2017-07-11
])
def test_weekday_after_next(text, expected):
    assert start(text) == ad(expected)
    assert _rem(text) == ""


def test_weekday_after_next_is_day_wide():
    assert span("the Saturday after next").width == timedelta(days=1)


# -- double-nested "the day after/before ..." -----------------------------

def test_double_day_after_tomorrow():
    # tomorrow = 06-28; the day after tomorrow = 06-29; one more day = 06-30
    assert start("the day after the day after tomorrow") == \
        ad(_MID + timedelta(days=3))                          # 2017-06-30
    assert _rem("the day after the day after tomorrow") == ""


def test_double_day_before_yesterday():
    # yesterday = 06-26; the day before yesterday = 06-25; one less = 06-24
    assert start("the day before the day before yesterday") == \
        ad(_MID - timedelta(days=3))                          # 2017-06-24
    assert _rem("the day before the day before yesterday") == ""


# -- regression pins: the SINGLE named-day idioms stay byte-identical ------

@pytest.mark.parametrize("text,expected", [
    ("the day after tomorrow", _MID + timedelta(days=2)),     # 2017-06-29
    ("the day before yesterday", _MID - timedelta(days=2)),   # 2017-06-25
])
def test_single_named_day_unchanged(text, expected):
    assert start(text) == ad(expected)
    assert _rem(text) == ""


# -- deferred: triple+ nesting composes only a single outer layer ---------

def test_triple_nest_composes_to_fixpoint():
    # the offset pass now iterates to a fixpoint, so every outer "the day
    # after" layer composes: tomorrow(06-28) +1 +1 +1 -> 07-01, nothing
    # stranded.  (See test_nl_nested_offset_fixpoint for arbitrary N.)
    r = parse("the day after the day after the day after tomorrow")
    assert r is not None
    assert r[0].start == ad(_MID + timedelta(days=4))         # 2017-07-01
    assert r[1] == ""
