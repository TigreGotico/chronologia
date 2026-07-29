# -*- coding: utf-8 -*-
"""Oracle sweep: Basque daypart-scoped clock hours (issues #281 / #283).

``goizeko Nak`` scopes the hour to the morning (N o'clock AM); ``arratsaldeko
Nak`` scopes it to the afternoon (N + 12).  The hour word is the inessive
absolutive-plural: ``hiru`` -> ``hiruretan`` (at 3).  Times are reckoned
prefer-future against the Tuesday 13:04 anchor -- morning hours have already
passed so they roll to the next day; afternoon hours are still ahead today.
The span is the clock minute ``[HH:00, HH:01)``.  Gold is independent
arithmetic.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start, start_end

#: inessive absolutive-plural hour surfaces, verified against the parser voc
HOUR_WORD = {
    3: "hiruretan", 4: "lauretan", 5: "bostetan", 6: "seietan",
    7: "zazpietan", 8: "zortzietan", 9: "bederatzietan",
    10: "hamarretan", 11: "hamaiketan",
}


def _next_at(hh):
    cand = ANCHOR.replace(hour=hh, minute=0, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return cand


# morning: goizeko N -> N:00 (AM)
GOIZ = [(f"goizeko {HOUR_WORD[n]}", n) for n in range(3, 12)]
# afternoon: arratsaldeko N -> (N+12):00
ARR = [(f"arratsaldeko {HOUR_WORD[n]}", n + 12) for n in range(3, 9)]


@pytest.mark.parametrize("text,hh", GOIZ + ARR)
def test_daypart_hour_start(text, hh):
    assert start(text) == ad(_next_at(hh))


@pytest.mark.parametrize("text,hh", GOIZ + ARR)
def test_daypart_hour_minute_span(text, hh):
    s, e = start_end(text)
    assert s == ad(_next_at(hh))
    assert e == ad(_next_at(hh) + timedelta(minutes=1))
