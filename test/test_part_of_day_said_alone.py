"""A part-of-day word said alone names its band (ruling 28).

pt "tarde" and "noite" are the whole text, so they read as the band of the
anchor's day, as "à tarde" and "à noite" do.  Inside a sentence the bare word
is not read: "tarde" is also the adverb "late".  it "stasera" is "questa
sera" (Treccani s.v. "stasera"), so it reads as the evening band with or
without a clock after it.  The bands are the CLDR 47 ones the locales cite:
pt afternoon 12:00-19:00 and evening 19:00-24:00, it sera 18:00-24:00.  Every
anchor lies inside or before its band, so the band stays on the anchor's day.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

PT_ANCHOR = datetime(2023, 1, 15, 12, 0)
IT_ANCHOR = datetime(2017, 6, 27, 13, 4)

BANDS = [
    ("tarde", "pt", PT_ANCHOR, datetime(2023, 1, 15, 12), datetime(2023, 1, 15, 19)),
    ("noite", "pt", PT_ANCHOR, datetime(2023, 1, 15, 19), datetime(2023, 1, 16)),
    ("manhã", "pt", datetime(2023, 1, 15, 5), datetime(2023, 1, 15, 6), datetime(2023, 1, 15, 12)),
    ("stasera", "it", IT_ANCHOR, datetime(2017, 6, 27, 18), datetime(2017, 6, 28)),
]


@pytest.mark.parametrize("text,lang,anchor,start,end", BANDS)
def test_a_part_of_the_day_alone_is_its_band(text, lang, anchor, start, end):
    found = extract_timespan(text, lang, anchor)
    assert (found.span.start.datetime(), found.span.end.datetime()) == (start, end)
    assert found.remainder == ""


def test_stasera_with_a_clock_leaves_no_remainder():
    found = extract_timespan("stasera alle 10", "it", IT_ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 6, 27, 22, 0)
    assert found.remainder == ""


@pytest.mark.parametrize("text", ["chegou tarde", "boa noite", "vou tarde para casa"])
def test_a_bare_pt_band_word_inside_a_sentence_is_not_read(text):
    assert extract_timespan(text, "pt", PT_ANCHOR) is None
