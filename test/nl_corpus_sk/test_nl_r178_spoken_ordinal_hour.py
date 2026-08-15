"""sk: the spoken clock names the coming hour with a feminine
locative ordinal agreeing with the elided "hodine" ("o druhej hodine" = at
two o'clock), the same toward-hour class Polish folds with its own feminine
locative table.  A past clock (before the anchor's time-of-day) rolls to
tomorrow -- the same convention the digit clock ("o 9 hodine") already
uses.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text,hour", [
    ("o jednej hodine", 1),
    ("o druhej hodine", 2),
    ("o štvrtej hodine", 4),
    ("o desiatej hodine", 10),
    ("o dvanástej hodine", 12),
])
def test_spoken_ordinal_hour_consumes_hour_word(text, hour):
    r = parse(text)
    assert r is not None
    # ANCHOR is 2017-06-27 13:04; every clock hour 1..12 read as 24h is
    # earlier in the day than the anchor's time-of-day, so it rolls forward
    # to the next calendar day.
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=hour, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""
