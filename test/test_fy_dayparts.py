# -*- coding: utf-8 -*-
"""West Frisian day parts.

CLDR ships no fy day-period rules, but West Frisian is co-official in Fryslan
and follows the Netherlands convention, so the band boundaries are Dutch (CLDR
nl: night 00-06, morning 06-12, afternoon 12-18, evening 18-24) and the surfaces
are Frisian (Frysk Wurdboek).  Gold is the band boundary, independent of the
extractor.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

_A = datetime(2017, 6, 27, 13, 4)   # a Tuesday afternoon


@pytest.mark.parametrize("surface,start_h,end_h", [
    ("moarns", 6, 12),      # 's morgens / morning
    ("middeis", 12, 18),    # 's middags / afternoon
    ("jûns", 18, 24),       # 's avonds / evening
    ("jûn", 18, 24),
    ("nachts", 0, 6),       # 's nachts / night
    ("nacht", 0, 6),
])
def test_fy_daypart_bands(surface, start_h, end_h):
    r = extract_timespan(surface, "fy", _A)
    assert r is not None
    s, e = r[0].start_datetime, r[0].end_datetime
    assert s.hour == start_h % 24 and s.date() == _A.date()
    assert (e.hour == end_h % 24) or (end_h == 24 and e.hour == 0)


def test_fy_middei_is_noon_landmark_not_the_afternoon_band():
    # the bare noun 'middei' is midday (the 12:00 clock-landmark), a point --
    # only the adverbial 'middeis' names the afternoon band.
    r = extract_timespan("middei", "fy", _A)
    assert r is not None
    assert r[0].start_datetime.hour == 12
    assert r[0].width.total_seconds() <= 60      # a landmark instant, not a 6h band


def test_fy_moarn_is_tomorrow_not_the_morning_band():
    # homograph guard: 'moarn' is "tomorrow" (named_day_1); only 'moarns' (with
    # the adverbial -s) names the morning band.
    r = extract_timespan("moarn", "fy", _A)
    assert r is not None
    assert r[0].start_datetime.date() == datetime(2017, 6, 28).date()
    assert r[0].width.days == 1                   # a whole day, not a 6h band


def test_fy_daypart_composes_with_a_named_day():
    # "moarn moarns" = tomorrow morning: the daypart narrows the named day.
    r = extract_timespan("moarn moarns", "fy", _A)
    assert r is not None
    assert r[0].start_datetime.isoformat() == "2017-06-28T06:00:00"
    assert r[0].end_datetime.isoformat() == "2017-06-28T12:00:00"
