"""Bare weekdays and this/next/last calendar periods.

``el martes`` names the next strictly-future occurrence of that weekday from the
anchor (Tuesday 2017-06-27), i.e. the following week.  Weeks are Monday-based.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import start_end, ad
from ._gen import WD

_ANCHOR = date(2017, 6, 27)  # Tuesday


@pytest.mark.parametrize("w,word", sorted(WD.items()))
def test_weekday_next_strict(w, word):
    offset = (w - _ANCHOR.weekday()) % 7 or 7
    d = datetime(2017, 6, 27) + timedelta(days=offset)
    s, e = start_end(f"el {word}")
    assert s == ad(d)
    assert e - s == timedelta(days=1)


_PERIODS = [
    ("esti mes", datetime(2017, 6, 1), datetime(2017, 7, 1)),
    ("el mes quevien", datetime(2017, 7, 1), datetime(2017, 8, 1)),
    ("el mes pasáu", datetime(2017, 5, 1), datetime(2017, 6, 1)),
    ("esti añu", datetime(2017, 1, 1), datetime(2018, 1, 1)),
    ("l'añu quevien", datetime(2018, 1, 1), datetime(2019, 1, 1)),
    ("l'añu pasáu", datetime(2016, 1, 1), datetime(2017, 1, 1)),
    ("esta selmana", datetime(2017, 6, 26), datetime(2017, 7, 3)),
    ("la selmana quevien", datetime(2017, 7, 3), datetime(2017, 7, 10)),
    ("la selmana pasada", datetime(2017, 6, 19), datetime(2017, 6, 26)),
]


@pytest.mark.parametrize("text,xs,xe", _PERIODS)
def test_this_next_last_period(text, xs, xe):
    s, e = start_end(text)
    assert (s, e) == (ad(xs), ad(xe))
