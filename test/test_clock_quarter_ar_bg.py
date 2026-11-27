# -*- coding: utf-8 -*-
"""Spelled quarter and half clocks in ar and bg.

Said at 13:04 on Tuesday 2017-06-27.  Gold by arithmetic: "four and a
quarter in the evening" is 16:00 + 15 min = 16:15; "nine less a quarter in
the evening" is 21:00 - 15 min = 20:45; "five days later at eight in the
evening" is 2017-07-02 20:00.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("lang,text,instant", [
    # ordinal hour + و-glued fraction, no الساعة before it
    ("ar", "عند الرابعة والربع مساءً", datetime(2017, 6, 27, 16, 15)),
    ("ar", "اليوم عند التاسعة والنصف صباحًا", datetime(2017, 6, 27, 9, 30)),
    # إلا + indefinite accusative ربعًا
    ("ar", "اليوم عند السابعة إلا ربعًا مساءً", datetime(2017, 6, 27, 18, 45)),
    ("ar", "في التاسعة إلا ربعًا مساءً", datetime(2017, 6, 27, 20, 45)),
    # "في تمام الساعة" after a day offset
    ("ar", "بعد خمسة أيام في تمام الساعة الثامنة مساءً",
     datetime(2017, 7, 2, 20, 0)),
    ("bg", "днес в пет и четвърт сутринта", datetime(2017, 6, 27, 5, 15)),
    ("bg", "днес в осем и четвърт вечерта", datetime(2017, 6, 27, 20, 15)),
])
def test_quarter_clock(lang, text, instant):
    assert extract_timespan(text, lang, ANCHOR).span.start.datetime() == instant


@pytest.mark.parametrize("lang,text", [
    ("ar", "فاز الفريق بالمرتبة الرابعة والنصف الآخر بالخامسة"),
    ("ar", "اشتريت ربع كيلو من التفاح"),
    ("bg", "една четвърт от хляба"),
])
def test_no_date_controls(lang, text):
    assert extract_timespan(text, lang, ANCHOR) is None
