"""A named day followed (or preceded) by a sub-day counted offset.

"today in an hour" is the anchor plus an hour: a counted offset keeps the
anchor clock and the named day only has to agree with it.  A named day the
offset does not land on ("tomorrow in an hour") is a contradiction and
parses to nothing.  Expected values come from ``datetime`` arithmetic on the
anchor, never from the parser.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)

#: (lang, text, offset) -- the same instant is named by the offset alone
SAME_DAY = [
    ("en", "today in an hour", timedelta(hours=1)),
    ("en", "today in 2 hours", timedelta(hours=2)),
    ("en", "today in 5 minutes", timedelta(minutes=5)),
    ("en", "in an hour today", timedelta(hours=1)),
    ("cs", "dnes za hodinu", timedelta(hours=1)),
    ("cs", "dneska za hodinu", timedelta(hours=1)),
    ("cs", "dneska za pět minut", timedelta(minutes=5)),
    ("hr", "danas za sat", timedelta(hours=1)),
    ("sk", "dnes za hodinu", timedelta(hours=1)),
    ("es", "hoy dentro de una hora", timedelta(hours=1)),
    ("de", "heute in einer stunde", timedelta(hours=1)),
    ("fr", "aujourd'hui dans une heure", timedelta(hours=1)),
    ("pt", "hoje daqui a uma hora", timedelta(hours=1)),
]


@pytest.mark.parametrize("lang,text,offset", SAME_DAY)
def test_named_day_with_subday_offset_is_anchor_plus_offset(lang, text, offset):
    got = extract_timespan(text, lang, ANCHOR)
    assert got is not None, text
    assert got.span.start == AstroDate.from_datetime(ANCHOR + offset)
    assert got.remainder == ""


def test_leading_words_stay_in_the_remainder():
    got = extract_timespan("remind me today in an hour", "en", ANCHOR)
    assert got.span.start == AstroDate.from_datetime(ANCHOR + timedelta(hours=1))
    assert got.remainder == "remind me"


#: another named day plus a counted offset is a contradiction at every
#: anchor, including when the offset lands on that day
CONTRADICTIONS = [
    ("en", "tomorrow in an hour", datetime(2017, 6, 27, 13, 4)),
    ("en", "yesterday in an hour", datetime(2017, 6, 27, 13, 4)),
    ("en", "in an hour tomorrow", datetime(2017, 6, 27, 13, 4)),
    ("en", "tomorrow in an hour", datetime(2017, 6, 27, 23, 30)),
    ("en", "in an hour tomorrow", datetime(2017, 6, 27, 23, 30)),
    ("en", "yesterday an hour ago", datetime(2017, 6, 27, 0, 10)),
    ("cs", "zítra za hodinu", datetime(2017, 6, 27, 23, 30)),
]


@pytest.mark.parametrize("lang,text,anchor", CONTRADICTIONS)
def test_other_named_day_contradicts_a_subday_offset(lang, text, anchor):
    assert extract_timespan(text, lang, anchor) is None


#: (lang, text, anchor, offset): "today" and an offset that crosses midnight
CROSSING = [
    ("en", "today in 5 hours", datetime(2017, 6, 27, 22, 0), timedelta(hours=5)),
    ("en", "today in an hour", datetime(2017, 6, 27, 23, 30), timedelta(hours=1)),
    ("en", "2 hours from now today", datetime(2017, 6, 27, 23, 30), timedelta(hours=2)),
    ("en", "an hour ago today", datetime(2017, 6, 27, 0, 10), -timedelta(hours=1)),
    ("cs", "za hodinu dnes", datetime(2017, 6, 27, 23, 30), timedelta(hours=1)),
    ("sk", "za hodinu dnes", datetime(2017, 6, 27, 23, 30), timedelta(hours=1)),
    ("hr", "za sat danas", datetime(2017, 6, 27, 23, 30), timedelta(hours=1)),
    ("es", "dentro de una hora hoy", datetime(2017, 6, 27, 23, 30), timedelta(hours=1)),
    ("de", "in einer stunde heute", datetime(2017, 6, 27, 23, 30), timedelta(hours=1)),
    ("fr", "dans une heure aujourd'hui", datetime(2017, 6, 27, 23, 30), timedelta(hours=1)),
    ("pt", "daqui a uma hora hoje", datetime(2017, 6, 27, 23, 30), timedelta(hours=1)),
    ("nl", "over een uur vandaag", datetime(2017, 6, 27, 23, 30), timedelta(hours=1)),
]


@pytest.mark.parametrize("lang,text,anchor,offset", CROSSING)
def test_offset_across_midnight_keeps_the_anchor_clock(lang, text, anchor, offset):
    got = extract_timespan(text, lang, anchor)
    assert got is not None, text
    assert got.span.start == AstroDate.from_datetime(anchor + offset)


def test_british_week_today_idiom_is_unchanged():
    got = extract_timespan("a week today", "en", ANCHOR)
    assert got.span.start == AstroDate.from_datetime(datetime(2017, 7, 4))
