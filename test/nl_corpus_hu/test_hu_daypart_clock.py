"""Hungarian daypart bands and the daypart + "N órakor" clock idiom.

A bare daypart word binds its band of the anchor day (reggel 06-12,
délelőtt 06-12, délután 12-18, este 18-21, éjjel 21-06).  When a whole hour
follows in the "N órakor" (at N o'clock) frame, the daypart fixes the 12-hour
half: délelőtt N -> N:00, délután N -> (N+12):00, este N -> (N+12):00.  The
resolved point rolls to the next future occurrence from the anchor.  Both the
half-of-day rule and the roll are applied here by hand, never by the parser.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, start_end


def _next_point(h, mi=0):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return cand


# -- bare daypart bands of the anchor day --------------------------------
@pytest.mark.parametrize("text,sh,eh,next_day", [
    ("reggel", 6, 12, False),
    ("délelőtt", 6, 12, False),
    ("délután", 12, 18, False),
    ("este", 18, 21, False),
    ("éjjel", 21, 6, True),
])
def test_bare_daypart_band(text, sh, eh, next_day):
    s = ANCHOR.replace(hour=sh, minute=0, second=0, microsecond=0)
    e = ANCHOR.replace(hour=eh, minute=0, second=0, microsecond=0)
    if next_day:
        e += timedelta(days=1)
    assert start_end(text) == (ad(s), ad(e))


# -- named-day + daypart band --------------------------------------------
@pytest.mark.parametrize("text,day_off,sh,eh", [
    ("ma reggel", 0, 6, 12),
    ("ma este", 0, 18, 21),
    ("holnap reggel", 1, 6, 12),
    ("holnap délután", 1, 12, 18),
    ("holnap este", 1, 18, 21),
    ("tegnap reggel", -1, 6, 12),
    ("tegnap este", -1, 18, 21),
    ("holnapután reggel", 2, 6, 12),
])
def test_named_day_daypart(text, day_off, sh, eh):
    base = ANCHOR + timedelta(days=day_off)
    s = base.replace(hour=sh, minute=0, second=0, microsecond=0)
    e = base.replace(hour=eh, minute=0, second=0, microsecond=0)
    assert start_end(text) == (ad(s), ad(e))


# -- daypart + "N órakor" point ------------------------------------------
_CLOCK = (
    [("délelőtt", n, n) for n in (8, 9, 10, 11)]
    + [("délután", n, n + 12) for n in (1, 2, 3, 4, 5, 6)]
    + [("este", n, n + 12) for n in (7, 8, 9, 10, 11)]
)


@pytest.mark.parametrize("part,n,h", _CLOCK)
def test_daypart_orakor(part, n, h):
    text = f"{part} {n} órakor"
    p = _next_point(h)
    assert start(text) == ad(p)
    assert start_end(text) == (ad(p), ad(p + timedelta(minutes=1)))
