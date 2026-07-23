"""Czech ordinal-toward-hour spoken clock.

Colloquial Czech names the coming hour with a genitive-feminine ordinal:
"půl deváté" == half OF the ninth == 08:30 (counted toward nine), "půl první"
== half toward one == 12:30 (twelve-hour reckoning).  Citation: Ústav pro
jazyk český AV ČR (Internetová jazyková příručka), telling the time.  Exact
H:MM, hand-derived.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, nomatch


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ("půl deváté", 8, 30),       # half of the ninth
    ("půl desáté", 9, 30),
    ("půl osmé", 7, 30),
    ("půl první", 12, 30),       # half toward one -> 12:30
    ("půl dvanácté", 11, 30),
])
def test_half_toward_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text", [
    "půl",              # bare half, no hour
])
def test_bare_fraction_without_hour_is_not_a_clock(text):
    nomatch(text)
