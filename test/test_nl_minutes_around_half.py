"""Dutch minutes counted from the half hour before the stated hour.

Team Taaladvies, "Kloktijden: acht uur zeventien / zeventien over acht /
dertien voor halfnegen" (taaladvies.net), lists 8.17 uur "dertien voor
halfnegen", 8.20 uur "tien voor halfnegen", 8.38 uur "acht over halfnegen" and
8.40 uur "tien over halfnegen".  The page reads "alles tussen 8.15 uur en 8.30
uur met voor halfnegen" and "alles tussen 8.30 uur en 8.45 uur met over
halfnegen".

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
    ("dertien voor half negen", (20, 17), ""),
    ("tien voor half negen", (20, 20), ""),
    ("acht over half negen", (20, 38), ""),
    ("tien over half negen", (20, 40), ""),
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


@pytest.mark.parametrize("text", [
    "om 30 over half 3", "om 30 voor half 3", "om 45 over half 3"])
def test_a_count_of_thirty_or_more_names_no_time(text):
    assert extract_timespan(text, "nl", ANCHOR) is None
