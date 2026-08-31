# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Arabic form ("من يناير إلى مارس") parses too -- the "from" lead (من) and the
"to" connector (إلى) ship per-locale (marker_from/marker_to), so range framing
is not English-only.  من / إلى are free words, so they tokenize as their own
tokens; the earlier date is always the span start, never inverted by
right-to-left reading order."""
from datetime import timedelta

import pytest

from chronologia import extract_timespan, extract_timespans

from ._corpus import ANCHOR, AstroDate, start_end, nomatch, remainder, span


@pytest.mark.parametrize("text,s,e", [
    ("يناير - مارس", (2017, 1, 1), (2017, 4, 1)),
    ("يونيو - أغسطس", (2017, 6, 1), (2017, 9, 1)),
    ("15 يناير - 20 يناير", (2018, 1, 15), (2018, 1, 21)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    ("من يناير إلى مارس", (2017, 1, 1), (2017, 4, 1)),
    ("من يونيو إلى أغسطس", (2017, 6, 1), (2017, 9, 1)),
    ("من 15 يناير إلى 20 يناير", (2018, 1, 15), (2018, 1, 21)),
])
def test_word_framed_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# -- adversarial: a bare range connector with no valid endpoints must not crash
# and must not fabricate a span.
@pytest.mark.parametrize("text", ["من", "إلى", "بين", "من إلى"])
def test_bare_connector_is_nomatch(text):
    nomatch(text)


# -- fused proclitic "and": Arabic writes the "و" (and) conjunction GLUED onto
# the word it precedes, with no space -- "بين يناير ومارس" ("between January
# andMarch").  The spaced and fused forms are the same range and must pin the
# same span; a bare word that legitimately starts with "و" ("وسط" mid) must
# NOT be mistaken for a glued endpoint.
@pytest.mark.parametrize("text,s,e", [
    ("بين يناير و مارس", (2017, 1, 1), (2017, 4, 1)),
    ("بين يناير ومارس", (2017, 1, 1), (2017, 4, 1)),
])
def test_fused_waw_range_endpoint(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


def test_wasat_is_not_split_as_fused_waw():
    # "وسط الشتاء" (mid-winter) starts with "و" but is not "و" + a month --
    # the guard must not mistake it for a glued range endpoint.  Independent
    # check (not a specific gold date): it must resolve as the single
    # mid-season phrase it is, consuming the whole utterance, rather than
    # splitting into a bogus "و" + "سط الشتاء" reading that strands text.
    assert remainder("وسط الشتاء") == ""


# -- fused waw closes classes beyond Gregorian months: Islamic-civil months,
# weekdays and dayparts also ship as single-word ar vocabulary and fuse the
# same way.  Each pins the exact span its already-working spaced-waw sibling
# resolves to.

# Islamic-civil (tabular arithmetic) calendar: month lengths alternate 30/29
# days by month parity (month 12 gets 30 in a leap year), the rule
# test_nl_other_calendars.py's hand-checked Hijri pins already rest on.
# Muharram 1442 = 2020-08-20..2020-09-18 (30 days, pinned there); Safar (an
# even month) is 29 days, so Safar 1442 = 2020-09-19..2020-10-17, end
# exclusive 2020-10-18.
@pytest.mark.parametrize("text,s,e", [
    ("بين محرم و صفر 1442", (2020, 8, 20), (2020, 10, 18)),
    ("بين محرم وصفر 1442", (2020, 8, 20), (2020, 10, 18)),
])
def test_fused_waw_islamic_month_range_endpoint(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# Weekday range: bare full weekday resolves to its next strictly-future
# occurrence (test_bare_weekday.py's rule, applied to both ends).  Anchor is
# Tuesday 2017-06-27 (weekday() == 1); Monday (idx 0) is 6 days ahead ->
# 2017-07-03, Friday (idx 4) counted from that Monday is 4 days ahead ->
# 2017-07-07, end exclusive 2017-07-08.
@pytest.mark.parametrize("text,s,e", [
    ("بين الإثنين و الجمعة", (2017, 7, 3), (2017, 7, 8)),
    ("بين الإثنين والجمعة", (2017, 7, 3), (2017, 7, 8)),
])
def test_fused_waw_weekday_range_endpoint(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# Daypart range: CLDR ar bands (Unicode CLDR 47/48 Day Period Rules, locale
# ar, transcribed in chronologia/dayparts.py; test_nl_daypart_sweep.py)
# morning 03-12, evening 18-24. Morning is anchored on the anchor's own civil
# day (2017-06-27, a Tuesday) since no deictic day is named; evening's 24:00
# close lands on the following civil day.
@pytest.mark.parametrize("text", ["بين الصباح و المساء", "بين الصباح والمساء"])
def test_fused_waw_daypart_range_endpoint(text):
    sp = span(text)
    assert sp.start_datetime == ANCHOR.replace(hour=3, minute=0, second=0,
                                               microsecond=0)
    assert sp.end_datetime == (ANCHOR + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0)


# Multiword Levantine month names ("كانون الأول" December) are NOT closed by
# this guard: splitting only the leading "و" off a multiword surface leaves a
# remainder the multiword-merge pass was never asked to re-glue, so the
# fused form still truncates.  Left open deliberately (tracked separately);
# pinned here so a future fix flips this from xfail to a real assertion.
@pytest.mark.xfail(reason="multiword month surfaces not covered by the fused-waw guard", strict=True)
def test_fused_waw_multiword_month_not_yet_closed():
    ss, ee = start_end("بين آذار وكانون الأول")
    assert ss == AstroDate(2017, 3, 1) and ee == AstroDate(2018, 1, 1)


def test_fused_waw_yields_two_mentions_not_one():
    # extract_timespans on a bare "MONTH وMONTH" utterance (no range lead)
    # now correctly reports two separate month mentions instead of folding
    # the second, fused month invisibly into the first's remainder.
    mentions = extract_timespans("يناير ومارس", "ar", ANCHOR)
    assert len(mentions) == 2
    assert mentions[0].span.start == AstroDate(2017, 1, 1)
    assert mentions[0].span.end == AstroDate(2017, 2, 1)
    assert mentions[1].span.start == AstroDate(2017, 3, 1)
    assert mentions[1].span.end == AstroDate(2017, 4, 1)


def test_fused_waw_bare_word_now_resolves_as_month():
    # Trade-off, not a defect: "ومارس" alone (no range lead) now resolves as
    # "و" + "مارس" (bare March) where it previously returned no match at all.
    # "مارس" is also the common verb "practised", so a bare fused reading is
    # ambiguous outside a range context; the guard accepts the temporal
    # reading unconditionally since it cannot see verb-vs-noun context.
    r = extract_timespan("ومارس", "ar", ANCHOR)
    assert r is not None
    assert r[0].start == AstroDate(2017, 3, 1) and r[0].end == AstroDate(2017, 4, 1)
    assert r[1] == "و"
