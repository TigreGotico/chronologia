"""Backward weekend references -- "the weekend before last" and
"<N> weekends ago", the weekend-unit members of the same backward-relative
family as the "the week before last" / "a <unit> ago" idioms.

These formerly resolved to the UPCOMING weekend and stranded their
qualifier: against the Tuesday 2017-06-27 13:04 anchor, "the weekend
before last" gave *this* weekend (07-01..07-03) with "before last" left
over, and "two weekends ago" gave the same upcoming weekend with
"weekends" stranded.  They must instead step BACKWARD by whole weekends.

The weekend is the Saturday-Sunday two-day span the locale already ships;
"the weekend before last" is the weekend two weekends into the past (the
weekend before *last* weekend); "<N> weekends ago" is the weekend N whole
weekends before the anchor's own (so one weekend ago == last weekend).
Expected spans come from independent calendar arithmetic, never by pinning
the parser.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, parse, span


def _expected(rel):
    """The Saturday-Sunday weekend ``rel`` weeks from the anchor's own."""
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    sat = (base - timedelta(days=base.weekday())
           + timedelta(days=5) + timedelta(weeks=rel))
    end = sat + timedelta(days=2)
    return (AstroDate(sat.year, sat.month, sat.day),
            AstroDate(end.year, end.month, end.day))


def _rem(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    return r[1]


# -- "the weekend before last": two weekends back -------------------------
#
# last weekend is Sat 06-24..Mon 06-26; the weekend before that is
# Sat 06-17..Mon 06-19 -- exactly rel == -2.

def test_the_weekend_before_last():
    assert (span("the weekend before last").start,
            span("the weekend before last").end) == _expected(-2)
    # hand-check the literal dates the arithmetic pins
    assert _expected(-2)[0] == AstroDate(2017, 6, 17)
    assert _expected(-2)[1] == AstroDate(2017, 6, 19)
    assert _rem("the weekend before last") == ""


def test_weekend_before_last_no_article():
    sp = span("weekend before last")
    assert (sp.start, sp.end) == _expected(-2)
    assert _rem("weekend before last") == ""


# -- "<N> weekends ago": N whole weekends back ----------------------------
#
# one weekend ago == last weekend (rel -1); two == rel -2; three == rel -3.

@pytest.mark.parametrize("text,rel", [
    ("a weekend ago", -1),          # 2017-06-24..06-26 (== last weekend)
    ("one weekend ago", -1),
    ("two weekends ago", -2),       # 2017-06-17..06-19
    ("three weekends ago", -3),     # 2017-06-10..06-12
])
def test_n_weekends_ago(text, rel):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel)
    assert _rem(text) == ""


def test_two_weekends_ago_literal_dates():
    sp = span("two weekends ago")
    assert (sp.start, sp.end) == (AstroDate(2017, 6, 17), AstroDate(2017, 6, 19))


# -- regression pins: the forward / this / last references stay put -------

@pytest.mark.parametrize("text,rel", [
    ("this weekend", 0),            # 2017-07-01..07-03
    ("next weekend", 1),            # 2017-07-08..07-10
    ("last weekend", -1),           # 2017-06-24..06-26 (most recent PAST)
    ("the weekend after next", 2),  # 2017-07-15..07-17 (skip one ahead)
])
def test_weekend_regression_pins(text, rel):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel)
