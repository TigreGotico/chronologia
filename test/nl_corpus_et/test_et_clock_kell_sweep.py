"""Estonian "kell N" whole-hour clock sweep.

``kell <cardinal>`` names the coming occurrence of that whole hour (prefer
future from the mission anchor Tuesday 13:04).  Cardinals one..twelve are
swept; every hour 1..12 lies before 13:04 so each resolves to the same hour
the following day.  The span is one minute wide.  Gold from independent
arithmetic.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start_end

CARDINALS = {
    1: "üks", 2: "kaks", 3: "kolm", 4: "neli", 5: "viis", 6: "kuus",
    7: "seitse", 8: "kaheksa", 9: "üheksa", 10: "kümme",
    11: "üksteist", 12: "kaksteist",
}


def _next_hour(h):
    cand = ANCHOR.replace(hour=h, minute=0, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return cand


@pytest.mark.parametrize("h,word", sorted(CARDINALS.items()))
def test_kell_whole_hour(h, word):
    s, e = start_end(f"kell {word}")
    base = _next_hour(h)
    assert s == ad(base)
    assert e == ad(base + timedelta(minutes=1))
