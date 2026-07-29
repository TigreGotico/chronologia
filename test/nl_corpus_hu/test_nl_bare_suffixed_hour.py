"""Hungarian bare "-kor" telling-time hour (the colloquial clock with "óra"
dropped and the temporal case suffix glued onto the numeral).

"háromkor" = at three, "nyolckor" = at eight: the everyday spoken form that
names a clock hour without the "óra" (o'clock) word.  Standalone it is a point
on the clock; with a daypart lead the daypart fixes the 12-hour half
(reggel N -> N:00, délután/este N -> (N+12):00) instead of stranding the
numeral and returning the band.  The resolved point rolls to the next future
occurrence from the anchor.  Both the hour and the roll are computed here by
independent arithmetic, never read back from the parser.

Source: -kor temporal case suffix (Wiktionary, https://en.wiktionary.org/wiki/-kor
#Hungarian); the cardinals are the standard telling-time forms (Magyar
helyesírás, Akadémiai Kiadó).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, start_end

#: bare "-kor" clock hour 1..12 -> value (independent of the parser).
_KOR = {
    "egykor": 1, "kettőkor": 2, "háromkor": 3, "négykor": 4, "ötkor": 5,
    "hatkor": 6, "hétkor": 7, "nyolckor": 8, "kilenckor": 9, "tízkor": 10,
    "tizenegykor": 11, "tizenkettőkor": 12,
}


def _next_point(h, mi=0):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return cand


@pytest.mark.parametrize("surface,n", sorted(_KOR.items()))
def test_bare_kor_standalone(surface, n):
    p = _next_point(n)
    assert start(surface) == ad(p)
    assert start_end(surface) == (ad(p), ad(p + timedelta(minutes=1)))


# reggel (morning) = am, so the hour stands; délután/este (afternoon/evening)
# = pm, so +12.  The daypart fixes the half and is consumed by the clock.
_LEAD = (
    [("reggel", s, n, n) for s, n in _KOR.items() if 1 <= n <= 11]
    + [("délután", s, n, n + 12) for s, n in _KOR.items() if 1 <= n <= 6]
    + [("este", s, n, n + 12) for s, n in _KOR.items() if 7 <= n <= 11]
)


@pytest.mark.parametrize("part,surface,n,h", _LEAD)
def test_daypart_lead_fixes_meridiem(part, surface, n, h):
    text = f"{part} {surface}"
    p = _next_point(h)
    assert start(text) == ad(p)
    assert start_end(text) == (ad(p), ad(p + timedelta(minutes=1)))
