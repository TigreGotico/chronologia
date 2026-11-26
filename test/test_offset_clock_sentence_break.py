# -*- coding: utf-8 -*-
"""A day offset takes a clock or a daypart only inside its own sentence.
Across ".", ";" or another sentence end, the offset keeps the anchor clock.
A comma does not stop the join.

Anchor Tuesday 27 June 2017 13:04; +2 days is 29 June 2017 13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
PLUS_TWO_DAYS = datetime(2017, 6, 29, 13, 4)

ACROSS_BREAK = [
    ("en", "in two days. at 3 pm we meet"),
    ("en", "in two days; at 3 pm we meet"),
    ("en", "in two days. tonight we pack"),
    ("de", "in zwei tagen. um 15 uhr treffen wir uns"),
    ("es", "dentro de dos días. a las tres de la tarde nos vemos"),
    ("pt", "daqui a dois dias. às três da tarde vemo-nos"),
]


@pytest.mark.parametrize("lang,text", ACROSS_BREAK)
def test_sentence_break_stops_offset_clock_join(lang, text):
    assert extract_timespan(text, lang, ANCHOR).span.start == PLUS_TWO_DAYS


def test_comma_keeps_offset_clock_join():
    r = extract_timespan("in two days, at 3 pm we meet", "en", ANCHOR)
    assert r.span.start == datetime(2017, 6, 29, 15, 0)
