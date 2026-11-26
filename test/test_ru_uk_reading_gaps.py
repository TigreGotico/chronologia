# -*- coding: utf-8 -*-
"""ru and uk reading gaps.

ru "в понедельник на следующей неделе в 8:15 утра" leaves nothing of the date
in the remainder.  uk "минулої ночі" is "last night" as ru "прошлой ночью" is:
"ночі" is the genitive singular of "ніч" (Wiktionary, ніч, declension table).
Last night is the night band of the same day, 00:00 to 04:00 (CLDR night band
in ``chronologia/dayparts.py``).  Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1038"
ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
def test_ru_weekday_of_next_week_keeps_nothing_of_the_date_in_the_remainder():
    found = extract_timespan(
        "в понедельник на следующей неделе в 8:15 утра", "ru", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 7, 3, 8, 15)
    assert found.remainder == ""


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_uk_last_night_is_the_night_band_of_today():
    found = extract_timespan("минулої ночі", "uk", ANCHOR)
    assert (found.span.start.datetime(), found.span.end.datetime()) == (
        datetime(2017, 6, 27, 0, 0), datetime(2017, 6, 27, 4, 0))
