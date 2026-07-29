"""Finnish bare ablative telling-time hour (the colloquial clock with "kello"
dropped and the -lta/-ltä ablative carried alone on the numeral).

"kolmelta" = at three, "yhdeksältä" = at nine: the everyday spoken form that
names a clock hour without the "kello" (o'clock) word.  Standalone it is a
point on the clock; with a trailing meridiem the half is fixed
(aamupäivällä N -> N:00, iltapäivällä N -> (N+12):00).  The resolved point rolls
to the next future occurrence from the anchor.  Both the hour and the roll are
computed here by independent arithmetic, never read back from the parser.

Source: -lta ablative case (Wiktionary, https://en.wiktionary.org/wiki/-lta
#Finnish); VISK §1237 (kellonajat) for the telling-time use.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, start_end

#: bare ablative clock hour 1..12 -> value (independent of the parser).
_ABL = {
    "yhdeltä": 1, "kahdelta": 2, "kolmelta": 3, "neljältä": 4, "viideltä": 5,
    "kuudelta": 6, "seitsemältä": 7, "kahdeksalta": 8, "yhdeksältä": 9,
    "kymmeneltä": 10, "yhdeltätoista": 11, "kahdeltatoista": 12,
}


def _next_point(h, mi=0):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return cand


@pytest.mark.parametrize("surface,n", sorted(_ABL.items()))
def test_bare_ablative_standalone(surface, n):
    p = _next_point(n)
    assert start(surface) == ad(p)
    assert start_end(surface) == (ad(p), ad(p + timedelta(minutes=1)))


# aamupäivällä (forenoon) = am, iltapäivällä (afternoon) = pm; the meridiem
# trails the hour in Finnish and is consumed by the clock.
_TRAIL = (
    [("aamupäivällä", s, n, n) for s, n in _ABL.items() if 1 <= n <= 11]
    + [("iltapäivällä", s, n, n + 12) for s, n in _ABL.items() if 1 <= n <= 6]
)


@pytest.mark.parametrize("part,surface,n,h", _TRAIL)
def test_trailing_meridiem_fixes_half(part, surface, n, h):
    text = f"{surface} {part}"
    p = _next_point(h)
    assert start(text) == ad(p)
    assert start_end(text) == (ad(p), ad(p + timedelta(minutes=1)))
