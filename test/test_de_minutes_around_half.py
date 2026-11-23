"""German minutes counted from the half hour before the stated hour.

DWDS, "halb", sense 1c (zeitlich): "es ist halb zwölf Uhr (= elf Uhr
dreißig)", "es ist zehn (Minuten) vor halb" and "es sind fünf Minuten bis,
nach halb".  So "M vor/nach halb H" is (H-1):30 minus or plus M.  Ruling 17
then picks the next reading of the twelve-hour time: the anchor is Saturday
2026-10-17 12:00.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_timespan

ANCHOR = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text, day, hm", [
    ("fünf vor halb drei", 17, (14, 25)),
    ("um fünf nach halb drei", 17, (14, 35)),
    ("zehn vor halb acht", 17, (19, 20)),
    ("um 5 vor halb 3", 17, (14, 25)),
    ("um 10 nach halb 8", 17, (19, 40)),
    ("fünf nach halb zwölf", 17, (23, 35)),
    ("zehn vor halb acht abends", 17, (19, 20)),
    # a day word keeps the written hour
    ("morgen um fünf vor halb neun", 18, (8, 25)),
    # the forms without minutes are unchanged
    ("halb drei", 17, (14, 30)),
    ("fünf vor drei", 17, (14, 55)),
])
def test_minutes_count_from_the_half_hour(text, day, hm):
    r = extract_timespan(text, "de", ANCHOR)
    assert (r.span.start, r.remainder) == (AstroDate(2026, 10, day, *hm), "")
