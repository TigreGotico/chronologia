"""Basque bare inessive telling-time hour (the plural hour numeral carrying the
-etan inessive case: "at N o'clock").

"hiruretan" = at three, "hamabietan" = at twelve: the everyday spoken form that
names a clock hour with the case glued onto the numeral.  Standalone it is a
point on the clock; with a leading meridiem the half is fixed
(goizeko N -> N:00, arratsaldeko N -> (N+12):00).  The resolved point rolls to
the next future occurrence from the anchor.  Both the hour and the roll are
computed here by independent arithmetic, never read back from the parser.

1 and 2 are two-word forms ("ordu batean", "ordu bietan"), outside this glued
series.  Source: -etan inessive plural (Wiktionary,
https://en.wiktionary.org/wiki/-etan#Basque); Euskaltzaindia, orduak.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, start_end

#: bare inessive clock hour 3..12 -> value (independent of the parser).
_INE = {
    "hiruretan": 3, "lauretan": 4, "bostetan": 5, "seietan": 6,
    "zazpietan": 7, "zortzietan": 8, "bederatzietan": 9, "hamarretan": 10,
    "hamaiketan": 11, "hamabietan": 12,
}


def _next_point(h, mi=0):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return cand


@pytest.mark.parametrize("surface,n", sorted(_INE.items()))
def test_bare_inessive_standalone(surface, n):
    p = _next_point(n)
    assert start(surface) == ad(p)
    assert start_end(surface) == (ad(p), ad(p + timedelta(minutes=1)))


# goizeko (of-the-morning) = am, arratsaldeko (of-the-afternoon) = pm; the
# meridiem leads the hour in Basque and is consumed by the clock.
_LEAD = (
    [("goizeko", s, n, n) for s, n in _INE.items() if 3 <= n <= 11]
    + [("arratsaldeko", s, n, n + 12) for s, n in _INE.items() if 3 <= n <= 6]
)


@pytest.mark.parametrize("part,surface,n,h", _LEAD)
def test_meridiem_lead_fixes_half(part, surface, n, h):
    text = f"{part} {surface}"
    p = _next_point(h)
    assert start(text) == ad(p)
    assert start_end(text) == (ad(p), ad(p + timedelta(minutes=1)))
