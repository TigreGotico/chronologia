"""Italian writes 21..99 as one word ("ventuno", "ventotto", "trentuno",
"ventitré"); the clock, the offset and the day of the month read them.

Wiktionary: ventuno, ventitré, ventotto, trentuno.  Anchor: Tuesday
2017-06-27 13:04; a clock names its next occurrence, an offset keeps the
anchor's time of day, a past day of the month rolls to next year.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


def _next(h, m=0):
    cand = ANCHOR.replace(hour=h, minute=m, second=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,m", [
    ("alle ventuno", 21, 0),
    ("alle ventidue", 22, 0),
    ("alle ventitré", 23, 0),
    ("alle ventuno e trenta", 21, 30),
])
def test_fused_compound_hour(text, h, m):
    res = parse(text)
    assert res is not None and res.remainder == "", f"{text!r} -> {res}"
    assert res[0].start == _next(h, m)
    assert res[0].start == parse(text.replace("ventuno", "21").replace(
        "ventidue", "22").replace("ventitré", "23"))[0].start


@pytest.mark.parametrize("text,delta,grain", [
    ("tra ventotto giorni", timedelta(days=28), timedelta(days=1)),
    ("tra quarantacinque minuti", timedelta(minutes=45), timedelta(minutes=1)),
])
def test_fused_compound_offset(text, delta, grain):
    res = parse(text)
    assert res is not None and res.remainder == ""
    assert res[0].start == ad(ANCHOR + delta)
    assert res[0].end == ad(ANCHOR + delta + grain)


@pytest.mark.parametrize("text,y,mo,d", [
    ("ventuno marzo", 2018, 3, 21),
    ("trentuno dicembre", 2017, 12, 31),
])
def test_fused_compound_day_of_month(text, y, mo, d):
    res = parse(text)
    assert res is not None and res.remainder == ""
    assert res[0].start == ad(datetime(y, mo, d))
    assert res[0].end == ad(datetime(y, mo, d) + timedelta(days=1))
