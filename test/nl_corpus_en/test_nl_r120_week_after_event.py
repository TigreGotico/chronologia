"""R120: "the week after/before <event>" resolves as a WEEK span, not a
single day.

Before this fix, the offset-from-reference pass (``anchored._try_offset``)
collapsed every unit -- including a bare, definite "the week" -- to the one
shifted civil day, exactly like "2 weeks after easter" or "3 days before
christmas".  That is correct arithmetic for a COUNTED offset ("a week
after", "2 weeks after"), but "the week after X" (bare unit, definite
article, no explicit count) names the calendar week itself -- the same
grain "the week of X" already widens to (``timespan._apply_week_of`` /
``resolver._week_span``).  This suite pins the fixed width and the sibling
constructions that must NOT change: counted offsets stay a point, "the
day after/before" stays a point, and the documented idiom quirks
("the week after next", "the day after next monday") stay untouched.

Expected values are hand-derived: the reference date's independently known
value (Easter/Christmas computus, same as ``test_nl_anchored_offset.py``),
shifted by the signed unit count, then widened to its Monday-start week by
plain ``timedelta`` arithmetic that never touches the parser.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse, span, start, start_end, nomatch

EASTER = date(2018, 4, 1)          # Sunday
CHRISTMAS = date(2017, 12, 25)     # Monday


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


def _week_of(d):
    """Independent Monday-start week containing ``d`` (mirrors the engine's
    own ``week_start='monday'`` convention, computed here from scratch)."""
    back = (d.weekday() - 0) % 7
    s = d - timedelta(days=back)
    return s, s + timedelta(days=7)


# -- the bare, definite "the week after/before X" widens to a week --------

@pytest.mark.parametrize("text,shifted", [
    ("the week after easter", EASTER + timedelta(days=7)),
    ("the week before christmas", CHRISTMAS - timedelta(days=7)),
])
def test_the_week_after_before_is_week_wide(text, shifted):
    exp_start, exp_end = _week_of(shifted)
    s, e = start_end(text)
    assert (s, e) == (_ad(exp_start), _ad(exp_end))
    assert span(text).width == timedelta(days=7)


def test_the_week_after_next_friday_unaffected_by_widening():
    # "the week after next friday" hits the SAME "next"-precedence quirk as
    # "the week after next monday"/"the day after next monday" below: "next"
    # between the marker and the weekday breaks the simple pre-amble scan,
    # so the phrase never reaches the week-widening path at all -- it reads
    # as the bare "next friday" reference with "the week after next" left as
    # leftover text.  This fix must not change that pre-existing shape.
    from ._corpus import ANCHOR
    next_friday = ANCHOR.date() + timedelta(
        days=(4 - ANCHOR.weekday()) % 7 or 7)
    r = parse("the week after next friday")
    assert r is not None
    assert r[0].start == _ad(next_friday)
    assert r[0].width == timedelta(days=1)
    assert r[1] == "the week after next"


# -- CONTROL: counted / indefinite weeks stay a single-day point ----------
# (plural/counted units, and the bare indefinite "a week", are plain
# arithmetic offsets -- unaffected by the week-widening.)

@pytest.mark.parametrize("text,expected", [
    ("two weeks after easter", EASTER + timedelta(days=14)),
    ("2 weeks after easter", EASTER + timedelta(days=14)),
    ("1 week after easter", EASTER + timedelta(days=7)),
    ("a week after easter", EASTER + timedelta(days=7)),
])
def test_counted_or_indefinite_week_stays_a_point(text, expected):
    s, e = start_end(text)
    assert s == _ad(expected)
    assert e == _ad(expected + timedelta(days=1))
    assert span(text).width == timedelta(days=1)


# -- CONTROL: "the day after/before X" is unaffected (day grain has no ----
# -- coarser widening -- it already names the atomic unit).

@pytest.mark.parametrize("text,expected", [
    ("the day after easter", EASTER + timedelta(days=1)),
    ("the day before christmas", CHRISTMAS - timedelta(days=1)),
])
def test_the_day_after_before_stays_a_point(text, expected):
    s, e = start_end(text)
    assert s == _ad(expected)
    assert span(text).width == timedelta(days=1)


# -- CONTROL: documented idiom quirks stay untouched -----------------------

def test_the_week_after_next_idiom_unchanged():
    # "the week after next" is a DEFERRED coarser-offset gap the grammar
    # does not spell (test_nl_backward_relative_day / test_nl_gap_residue) --
    # this fix must not accidentally start matching it.
    nomatch("the week after next")


def test_the_day_after_next_monday_idiom_unchanged():
    # pinned en idiom-precedence quirk: "the day after next" (named_day
    # idiom, anchor + 2 days) wins over composing "monday" as its reference,
    # stranding "monday" in the remainder -- untouched by this fix.
    from ._corpus import ANCHOR
    day_after_next = ANCHOR.date() + timedelta(days=2)
    r = parse("the day after next monday")
    assert r is not None
    s = r[0].start
    assert s == _ad(day_after_next)
    assert r[0].width == timedelta(days=1)
    assert r[1] == "monday"
