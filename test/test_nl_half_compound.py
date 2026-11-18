"""Dutch writes "half" and the hour as one word.

Team Taaladvies, "Kloklezen, kloktijden lezen": 6.30 uur is "halfzeven",
6.20 uur "tien voor halfzeven" and 6.40 uur "tien over halfzeven".  The one
word reads as the two words "half zeven" do.  Ruling 17 picks the next
reading of the twelve-hour time: the anchor is Saturday 2026-10-17 12:00.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_timespan

ANCHOR = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text, day, hm", [
    # 06:30 has passed, so 18:30
    ("halfzeven", 17, (18, 30)),
    ("om halfzeven", 17, (18, 30)),
    ("Halfzeven", 17, (18, 30)),
    ("tien voor halfzeven", 17, (18, 20)),
    ("tien over halfzeven", 17, (18, 40)),
    ("zeven over halfzeven", 17, (18, 37)),
    ("dertien voor halfnegen", 17, (20, 17)),
    # 00:30 has passed and 12:30 is ahead
    ("halfeen", 17, (12, 30)),
    ("halféén", 17, (12, 30)),
    ("halftwaalf", 17, (23, 30)),
    ("vijf voor halfacht 's avonds", 17, (19, 25)),
    ("morgenochtend om halfacht", 18, (7, 30)),
])
def test_one_word_half_hour(text, day, hm):
    r = extract_timespan(text, "nl", ANCHOR)
    assert (r.span.start, r.remainder) == (AstroDate(2026, 10, day, *hm), "")


@pytest.mark.parametrize("text", ["halfjaar", "een halfjaar", "halfvol"])
def test_other_half_words_stay_whole(text):
    assert extract_timespan(text, "nl", ANCHOR) is None
