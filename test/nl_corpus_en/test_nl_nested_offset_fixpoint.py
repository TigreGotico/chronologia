"""Nested day-offset composition iterates to a fixpoint (arbitrary N-nesting).

PR #314 made the DOUBLE nest compose ("the day after the day after tomorrow"
-> +3 from the anchor: tomorrow +1 +1).  It composed exactly one outer offset
layer, so TRIPLE and deeper nests stranded the outermost "the day after" /
"the day before" marker in the remainder -- a silent-wrong.

The composition now iterates to a fixpoint: each pass consumes one more outer
"day after"/"day before" layer, so nesting of any depth resolves, while
depth<=2 and non-nested phrases are byte-identical (their second pass finds
nothing to compose and stops).

Anchor 2017-06-27 (Tue, 13:04):

    tomorrow  = 2017-06-28        yesterday = 2017-06-26
    the day after tomorrow        = 2017-06-29   (+1)
    ... the day after ...  (x n)  = 2017-06-28 + n
    ... the day before ... (x n)  = 2017-06-26 - n
"""
from datetime import date, timedelta

import pytest

from ._corpus import start

TOMORROW = date(2017, 6, 28)
YESTERDAY = date(2017, 6, 26)


def _ad(d):
    from ._corpus import AstroDate
    return AstroDate(d.year, d.month, d.day)


def _after(n):
    return "the day after " * n + "tomorrow"


def _before(n):
    return "the day before " * n + "yesterday"


# -- regression pins: depth 1 and 2 are UNCHANGED --------------------------

@pytest.mark.parametrize("text,expected", [
    ("the day after tomorrow", TOMORROW + timedelta(days=1)),        # +1 -> 29
    (_after(2), TOMORROW + timedelta(days=2)),                        # +2 -> 30
    ("the day before yesterday", YESTERDAY - timedelta(days=1)),      # -1 -> 25
    (_before(2), YESTERDAY - timedelta(days=2)),                      # -2 -> 24
])
def test_depth_1_and_2_unchanged(text, expected):
    assert start(text) == _ad(expected)


# -- triple+ nesting now composes the outermost layer ----------------------

@pytest.mark.parametrize("n", [3, 4, 5, 8])
def test_deep_after_nesting(n):
    # tomorrow(28) + n days, rolling into July past June's 30 days
    assert start(_after(n)) == _ad(TOMORROW + timedelta(days=n))


@pytest.mark.parametrize("n", [3, 4, 5, 8])
def test_deep_before_nesting(n):
    assert start(_before(n)) == _ad(YESTERDAY - timedelta(days=n))


# -- named exact-date pins from the task -----------------------------------

def test_triple_after_exact():
    assert start(_after(3)) == _ad(date(2017, 7, 1))


def test_triple_before_exact():
    assert start(_before(3)) == _ad(date(2017, 6, 23))


# -- adversarial deep nest MUST terminate (cap backstop), never hang/raise --

def test_adversarial_deep_nest_terminates():
    text = "the day after " * 50 + "tomorrow"
    # must return without raising and within the iteration cap; result is a
    # sane date or None -- we only require termination + no exception here.
    from ._corpus import parse
    r = parse(text)
    assert r is None or r[0].start is not None
