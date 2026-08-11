# -*- coding: utf-8 -*-
"""R116: a day-part composing with an adjacent anchoring date must consume
the connector between them, not strand it in the remainder.

"the morning of the day after tomorrow" resolves the daypart_ref ("morning")
and the anchored date ("the day after tomorrow") as one composed reading (the
morning band narrowed onto that day) -- see :func:`compose_date_daypart` in
chronologia/extract/resolver.py and the composition gate in
:func:`chronologia.extract.timespan._compose`.  Composition only claims the
two matches' own token spans, never the connector word stitching them
("of") nor the article opening the day-part phrase ("the") -- both surfaced
as a dangling, nonsensical remainder ("the of") even though the SPAN itself
was correct.  The fix extends the composed reading's consumed tokens with
the glue connector between the two matches (and a lone opening article, if
one directly precedes the day-part) whenever composition actually succeeds.

Gold spans are derived by hand from the CLDR day-period bands (morning
06:00-12:00, afternoon 12:00-18:00, evening 18:00-21:00, night 21:00-06:00
next day) and plain calendar arithmetic off the shared corpus ANCHOR
(2017-06-27, a Tuesday) -- never read back from the parser.
"""
from datetime import timedelta

from ._corpus import ANCHOR, AstroDate, parse


def _day(dt):
    return AstroDate(dt.year, dt.month, dt.day)


def test_daypart_of_anchored_date_consumes_connector():
    text = "Let's meet the morning of the day after tomorrow"
    r = parse(text)
    assert r is not None
    day = ANCHOR + timedelta(days=2)               # "the day after tomorrow"
    assert r.span.start == AstroDate(day.year, day.month, day.day, 6, 0, 0)
    assert r.span.end == AstroDate(day.year, day.month, day.day, 12, 0, 0)
    assert r.remainder == "Let's meet"


def test_evening_of_next_friday_consumes_connector():
    r = parse("the evening of next friday")
    assert r is not None
    day = ANCHOR + timedelta(days=3)                # Tue -> next Friday
    assert r.span.start == AstroDate(day.year, day.month, day.day, 18, 0, 0)
    assert r.span.end == AstroDate(day.year, day.month, day.day, 21, 0, 0)
    assert r.remainder == ""


def test_afternoon_of_march_3rd_consumes_connector():
    r = parse("the afternoon of March 3rd")
    assert r is not None
    assert r.span.start == AstroDate(2018, 3, 3, 12, 0, 0)   # next March 3rd
    assert r.span.end == AstroDate(2018, 3, 3, 18, 0, 0)
    assert r.remainder == ""


def test_night_of_day_before_yesterday_crosses_midnight_and_is_clean():
    r = parse("the night of the day before yesterday")
    assert r is not None
    day = ANCHOR - timedelta(days=2)                # "the day before yesterday"
    nxt = day + timedelta(days=1)
    assert r.span.start == AstroDate(day.year, day.month, day.day, 21, 0, 0)
    assert r.span.end == AstroDate(nxt.year, nxt.month, nxt.day, 6, 0, 0)
    assert r.remainder == ""


def test_non_temporal_of_survives_when_nothing_composes():
    # "of" here glues a possessive noun phrase, not a daypart to a date --
    # no composition happens, so the connector must NOT be swallowed.
    r = parse("the king of Spain arrives tomorrow")
    assert r is not None
    day = ANCHOR + timedelta(days=1)
    assert r.span.start == AstroDate(day.year, day.month, day.day)
    assert r.span.end == AstroDate(day.year, day.month, day.day) + timedelta(days=1)
    assert r.remainder == "the king of Spain arrives"


def test_bare_daypart_composition_unaffected():
    # a daypart glued directly onto a bare relative day, with NO connector
    # or article between the two spans -- must keep its long-standing empty
    # remainder (regression guard for the composition-glue change).
    r = parse("yesterday morning")
    assert r is not None
    day = ANCHOR - timedelta(days=1)
    assert r.span.start == AstroDate(day.year, day.month, day.day, 6, 0, 0)
    assert r.span.end == AstroDate(day.year, day.month, day.day, 12, 0, 0)
    assert r.remainder == ""
