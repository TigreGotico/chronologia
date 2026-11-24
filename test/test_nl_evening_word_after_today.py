# -*- coding: utf-8 -*-
"""nl: an evening word beside a digit clock keeps the evening half.

Ruling 27: "A locale's own morning or evening word beside a digit clock decides
the half."  "'s avonds" puts "om 8:00" in the evening and "vandaag" keeps the
anchor's day, so the reading is 20:00 on 2017-06-27 whatever the order of
the words.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1081"


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_the_evening_word_after_today_keeps_the_pm_half():
    found = extract_timespan(
        "om 8:00 vandaag 's avonds", "nl", datetime(2017, 6, 27, 5, 0))
    assert found.span.start.datetime() == datetime(2017, 6, 27, 20, 0)
