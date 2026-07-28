# -*- coding: utf-8 -*-
"""Oracle sweep: relative-day + daypart band (bg).

A deictic day word (днес/утре/вчера) combined with a CLDR day-period band
(сутрин 04-14, следобед 14-18, вечер 18-22, нощем 22-04) yields that band on
the referenced calendar day.  Gold is independent arithmetic off the anchor
date; the parser is never consulted.  The three (day, band) surfaces already
pinned in test_nl_daypart.py are skipped here to avoid duplicates.

Anchor 2017-06-27 (Tuesday, 13:04).
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, span

ANCHOR = datetime(2017, 6, 27)
DAYS = {"днес": 0, "утре": 1, "вчера": -1}
# band -> (start_hour, end_hour, end_next_day)
BANDS = {"сутрин": (4, 14, False), "следобед": (14, 18, False),
         "вечер": (18, 22, False), "нощем": (22, 4, True)}
EXISTING = {("днес", "сутрин"), ("вчера", "вечер"), ("утре", "следобед")}

CASES = [(dw, bw) for dw in DAYS for bw in BANDS
         if (dw, bw) not in EXISTING]


@pytest.mark.parametrize("day_word,band_word", CASES,
                         ids=[f"{d} {b}" for d, b in CASES])
def test_daypart_band(day_word, band_word):
    sh, eh, nxt = BANDS[band_word]
    base = ANCHOR + timedelta(days=DAYS[day_word])
    start = base.replace(hour=sh)
    end = (base + timedelta(days=1) if nxt else base).replace(hour=eh)
    phrase = f"{day_word} {band_word}"
    s = span(phrase)
    assert s.start == AstroDate(start.year, start.month, start.day, start.hour), phrase
    assert s.end == AstroDate(end.year, end.month, end.day, end.hour), phrase
