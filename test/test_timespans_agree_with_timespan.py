"""extract_timespans reads a text as extract_timespan does.

da and sv "jul" is Christmas (Den Danske Ordbog "jul"; Svenska Akademiens
ordbok "jul"), so both edges read 25 December.  "one in the afternoon" is
13:00.  Anchor: Tuesday 2017-06-27 13:04 Europe/Lisbon.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from chronologia import extract_timespan, extract_timespans

ISSUE = "https://github.com/TigreGotico/chronologia/issues/995"
ANCHOR = datetime(2017, 6, 27, 13, 4, tzinfo=ZoneInfo("Europe/Lisbon"))


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang", ["da", "sv"])
def test_jul_is_christmas_from_extract_timespans(lang):
    mentions = extract_timespans("jul", lang, ANCHOR)
    assert [m.span.start.datetime() for m in mentions] == [
        datetime(2017, 12, 25)]


def test_one_in_the_afternoon_starts_at_13_00_in_extract_timespan():
    found = extract_timespan(
        "how is the weather supposed to look this Friday at one in the "
        "afternoon", "en", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 6, 30, 13, 0)
