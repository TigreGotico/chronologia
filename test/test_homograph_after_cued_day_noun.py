"""A noun that cues a "today's" adjective is no cue for a date homograph."""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("lang,text", [
    ("pt-PT", "as sessões verão o filme"),
    ("pt-PT", "as reuniões verão mudanças"),
    ("pt-PT", "a data verão depois"),
    ("uk", "матч лютий"),
    ("uk", "обід лютий"),
    ("uk", "зустріч лютим поглядом"),
])
def test_cued_day_noun_leaves_the_homograph_alone(lang, text):
    assert extract_timespan(text, lang, ANCHOR) is None


@pytest.mark.parametrize("lang,text,month", [
    ("pt-PT", "no verão", 6),
    ("uk", "у лютому", 2),
])
def test_control_a_cued_homograph_reads(lang, text, month):
    assert extract_timespan(text, lang, ANCHOR).span.start.month == month
