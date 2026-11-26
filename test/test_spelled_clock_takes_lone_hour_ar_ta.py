# -*- coding: utf-8 -*-
"""A spelled ar or ta clock takes the lone-hour reading of its digit twin.

Ruling 23: "Speech recognition writes a spoken 'three thirty' as '3:30', so
the two forms must read the same."  Said at 13:04 on Tuesday 2017-06-27, the
digit twin "6:30" is 18:30 the same day, so "الساعة السادسة والنصف" is
18:30 too; ta "9:30" is 21:30, "9:15" 21:15, "3:10" 15:10 and "5:45" 17:45.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1072"
ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,instant", [
    ("ar", "الساعة السادسة والنصف", datetime(2017, 6, 27, 18, 30)),
    ("ta", "ஒன்பதரை மணி", datetime(2017, 6, 27, 21, 30)),
    ("ta", "ஒன்பதே கால்", datetime(2017, 6, 27, 21, 15)),
    ("ta", "மூன்று மணிக்கு பத்து நிமிடம் மேல்", datetime(2017, 6, 27, 15, 10)),
    ("ta", "ஆறு மணிக்கு பதினைந்து நிமிடம் குறைவு",
     datetime(2017, 6, 27, 17, 45)),
])
def test_a_spelled_clock_reads_as_its_digit_twin(lang, text, instant):
    assert extract_timespan(text, lang, ANCHOR).span.start.datetime() == instant
