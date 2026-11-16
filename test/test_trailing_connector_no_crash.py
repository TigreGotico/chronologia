"""A trailing "and" after an offset is left over; it does not raise.

The compound-offset scanner reads "[and] NUM UNIT" chunks after an offset.
A text that ends on the connector has no chunk after it, and the reader
must return the offset with the connector in the remainder.  Anchor Friday
30 January 2026, 10:00.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan
from chronologia.events import extract_event

ANCHOR = datetime(2026, 1, 30, 10, 0)


@pytest.mark.parametrize("lang, text, offset, left", [
    ("en", "in two weeks and", timedelta(weeks=2), "and"),
    ("en", "in 3 months and", None, "and"),
    ("de", "in zwei stunden und", timedelta(hours=2), "und"),
    ("fr", "dans deux semaines et", timedelta(weeks=2), "et"),
    ("pt", "daqui a duas semanas e", timedelta(weeks=2), "e"),
    ("nl", "over twee weken en", timedelta(weeks=2), "en"),
])
def test_an_offset_before_a_trailing_and_leaves_the_and(lang, text, offset,
                                                         left):
    got = extract_timespan(text, lang, anchor=ANCHOR)
    # 30 January + 3 months is 30 April
    start = ANCHOR + offset if offset else datetime(2026, 4, 30, 10, 0)
    assert (got.span.start, got.remainder) == (start, left)


@pytest.mark.parametrize("lang, text", [
    ("en", "in 3 months and"),
    ("es", "2 próximas semanas y 3 dias"),
])
def test_an_event_with_a_trailing_and_takes_the_span_reading(lang, text):
    ev = extract_event(text, lang, anchor=ANCHOR)
    assert ev.span.start == extract_timespan(text, lang, anchor=ANCHOR).span.start
