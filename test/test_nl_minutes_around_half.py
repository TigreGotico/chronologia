"""Dutch minutes counted from the half hour before the stated hour.

Team Taaladvies, "Kloklezen, kloktijden lezen": 6.20 uur is "tien voor
halfzeven", 6.37 uur "zeven over halfzeven", 6.40 uur "tien over halfzeven".
So "M voor/over half H" is (H-1):30 minus or plus M.  Ruling 17 then picks
the next reading of the twelve-hour time: the anchor is 12:00, so every time
below falls in the afternoon or evening of the same day.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_timespan

ANCHOR = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text, hm, rest", [
    ("vijf voor half vier", (15, 25), ""),
    ("om 5 voor half 3", (14, 25), ""),
    ("om vijf voor half drie", (14, 25), ""),
    ("wekker om tien over half drie", (14, 40), "wekker"),
    ("om 10 over half 3", (14, 40), ""),
    ("om tien over half drie", (14, 40), ""),
    ("tien over half drie", (14, 40), ""),
    ("om kwart over half 9", (20, 45), ""),
    ("om kwart over half negen", (20, 45), ""),
    ("om kwart over half drie", (14, 45), ""),
    ("kwart over half negen", (20, 45), ""),
    ("om kwart voor half 9", (20, 15), ""),
    ("om kwart voor half negen", (20, 15), ""),
    ("kwart voor half negen", (20, 15), ""),
    ("wekker om kwart over half 9", (20, 45), "wekker"),
    ("tien voor half zeven", (18, 20), ""),
    ("dertien voor half zeven", (18, 17), ""),
    ("zeven over half zeven", (18, 37), ""),
])
def test_minutes_count_from_the_half_hour(text, hm, rest):
    r = extract_timespan(text, "nl", ANCHOR)
    assert (r.span.start, r.remainder) == (AstroDate(2026, 10, 17, *hm), rest)


@pytest.mark.parametrize("text, hm", [
    ("half drie", (14, 30)),
    ("tien over drie", (15, 10)),
    ("kwart voor negen", (20, 45)),
])
def test_the_plain_forms_stay(text, hm):
    assert extract_timespan(text, "nl", ANCHOR).span.start == AstroDate(2026, 10, 17, *hm)
