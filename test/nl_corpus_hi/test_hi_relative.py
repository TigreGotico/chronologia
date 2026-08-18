"""Offsets, relative periods, dayparts and seasons -- all markers postposed.

An offset is NUM UNIT MARKER: "तीन दिन पहले" is three days ago and "दो हफ़्ते
बाद" two weeks hence.  Both marker words are CLDR 47's own relative-time
patterns for locale hi ("{0} दिन पहले" past, "{0} दिन में" future), and बाद is
en.wiktionary's everyday synonym of the latter ("एक दिन बाद" -- one day later).

The unit noun counted by a numeral stands in the OBLIQUE case, which for the
-आ stems is a plain -ए (दो घंटे, तीन हफ़्ते), so both the direct and the oblique
form of every doublet is exercised.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, remainder, span, start


@pytest.mark.parametrize("text,days", [
    ("तीन दिन पहले", -3),
    ("एक दिन पहले", -1),
    ("दस दिन पहले", -10),
    ("तीन दिन बाद", 3),
    ("तीन दिन में", 3),
    ("एक दिन बाद", 1),
    ("पंद्रह दिन बाद", 15),
])
def test_day_offsets_run_both_ways(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,delta", [
    ("दो हफ़्ते बाद", timedelta(weeks=2)),
    ("दो सप्ताह बाद", timedelta(weeks=2)),
    ("तीन हफ़्ते पहले", timedelta(weeks=-3)),
    ("दस घंटे बाद", timedelta(hours=10)),
    ("पाँच घंटे पहले", timedelta(hours=-5)),
    ("बीस मिनट बाद", timedelta(minutes=20)),
    ("तीस मिनट पहले", timedelta(minutes=-30)),
    ("पाँच सेकंड पहले", timedelta(seconds=-5)),
])
def test_unit_offsets(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("direct,oblique", [
    ("एक घंटा बाद", "एक घंटे बाद"),
    ("एक हफ़्ता बाद", "एक हफ़्ते बाद"),
    ("एक महीना बाद", "एक महीने बाद"),
])
def test_the_oblique_unit_form_reads_the_same(direct, oblique):
    """The counted noun's oblique -ए is a fact of the noun, so both forms of
    an ā-stem unit name the same offset."""
    assert span(direct).start == span(oblique).start


@pytest.mark.parametrize("text,years", [
    ("दो साल बाद", 2), ("दो वर्ष बाद", 2), ("दो बरस बाद", 2),
    ("पाँच साल पहले", -5),
])
def test_the_year_doublets_agree(text, years):
    s = start(text)
    assert s.year == ANCHOR.year + years


@pytest.mark.parametrize("text,y,m", [
    ("अगला महीना", 2017, 7), ("पिछला महीना", 2017, 5), ("इस महीने", 2017, 6),
    ("अगला माह", 2017, 7), ("पिछला माह", 2017, 5),
])
def test_relative_month(text, y, m):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (y, m, 1)


@pytest.mark.parametrize("text,monday", [
    ("अगला सप्ताह", (2017, 7, 3)),
    ("पिछला सप्ताह", (2017, 6, 19)),
    ("इस हफ़्ते", (2017, 6, 26)),
    ("अगले हफ़्ते", (2017, 7, 3)),
])
def test_relative_week_starts_on_monday(text, monday):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == monday
    assert (s.end - s.start).days == 7


@pytest.mark.parametrize("text,year", [
    ("अगला वर्ष", 2018), ("पिछला वर्ष", 2016), ("इस वर्ष", 2017),
    ("अगला साल", 2018), ("पिछले साल", 2016),
])
def test_relative_year(text, year):
    assert span(text).start.year == year


@pytest.mark.parametrize("text,h0,h1", [
    ("सुबह", 4, 12), ("दोपहर", 12, 16), ("शाम", 16, 20),
])
def test_daypart_bands_are_the_cldr_ones(text, h0, h1):
    """CLDR 47 locale hi: morning 04-12, afternoon 12-16, evening 16-20,
    night 20-04."""
    s = span(text)
    assert s.start.hour == h0
    assert (s.end - s.start).seconds == (h1 - h0) * 3600


def test_the_night_band_crosses_midnight():
    s = span("रात")
    assert s.start.hour == 20
    assert s.end.hour == 4


@pytest.mark.parametrize("text", ["शाम को", "सुबह को", "दोपहर को"])
def test_the_daypart_postposition_is_consumed(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,m0,m1", [
    ("बसंत", 3, 6), ("वसंत", 3, 6),
    ("गर्मी", 6, 9), ("ग्रीष्म", 6, 9),
    ("पतझड़", 9, 12), ("शरद", 9, 12),
])
def test_northern_hemisphere_seasons(text, m0, m1):
    s = span(text)
    assert s.start.month == m0 and s.end.month == m1


def test_winter_wraps_the_year():
    s = span("सर्दी")
    assert s.start.month == 12 and s.end.month == 3


def test_weekend():
    s = span("सप्ताहांत")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 1)
    assert (s.end - s.start).days == 2


@pytest.mark.parametrize("text", ["पहले", "बाद", "दिन पहले", "में"])
def test_a_marker_with_nothing_to_measure_is_not_a_time(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", [
    "3 दिन पहले", "через 3 дня", "hace 3 días", "3 days ago",
])
def test_only_the_hindi_phrasing_reads_as_an_offset(text):
    """The first is Hindi and must resolve; the rest are other languages'
    wordings and must not be read as Hindi offsets."""
    r = parse(text)
    if text.startswith("3 दिन"):
        assert start(text) == ad(ANCHOR - timedelta(days=3))
    else:
        assert r is None or r[0].start.date() != (ANCHOR - timedelta(days=3)).date()
