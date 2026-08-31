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
    # CLDR ar morning is [03:00, 12:00), not chronologia's default [06:00, 12:00)
    ("هذا الصباح", "2017-06-27", 3),    # this morning
    ("صباح اليوم", "2017-06-27", 3),    # this morning (of today)
    ("مساء أمس", "2017-06-26", 18),     # yesterday evening
    ("مساء الأمس", "2017-06-26", 18),
])
def test_ar_daypart(text, date, h0):
    s = _s(text)
    assert s.start_datetime.date().isoformat() == date
    assert s.start_datetime.hour == h0
    assert (s.end_datetime - s.start_datetime).total_seconds() < 24 * 3600


def test_ar_morning_uses_ar_band_not_default():
    # Adversarial: CLDR ar morning starts at 03:00, chronologia's default
    # (lang=None) morning starts at 06:00. A loader that mis-keys the ar
    # surfaces (drops the _ar suffix from the daypart_*.voc filename) falls
    # through to the default band and this would wrongly read 06:00.
    s = _s("هذا الصباح")
    assert s.start_datetime.hour == 3
    assert s.start_datetime.hour != 6
