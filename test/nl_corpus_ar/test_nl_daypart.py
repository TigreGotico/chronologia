# -*- coding: utf-8 -*-
"""Arabic dayparts. Surfaces confirmed by native speaker athmanemokraoui
(TigreGotico/chronologia#268); CLDR 47 bands. Anchor Tue 2017-06-27."""
from datetime import datetime
import pytest
from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _s(t):
    r = extract_timespan(t, "ar", ANCHOR)
    assert r is not None and r[0] is not None, f"{t!r} did not parse"
    assert r[1] == "", f"{t!r} left remainder {r[1]!r}"
    return r[0]


@pytest.mark.parametrize("text,date,h0", [
    ("هذا الصباح", "2017-06-27", 6),    # this morning
    ("صباح اليوم", "2017-06-27", 6),    # this morning (of today)
    ("مساء أمس", "2017-06-26", 18),     # yesterday evening
    ("مساء الأمس", "2017-06-26", 18),
])
def test_ar_daypart(text, date, h0):
    s = _s(text)
    assert s.start_datetime.date().isoformat() == date
    assert s.start_datetime.hour == h0
    assert (s.end_datetime - s.start_datetime).total_seconds() < 24 * 3600
