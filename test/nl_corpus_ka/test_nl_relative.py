"""Offsets, which Georgian builds with a POSTPOSITION on a genitive noun.

"სამი თვის წინ" is three months ago: the count leads, the unit follows it in
the genitive singular, and the marker წინ closes the phrase.  შემდეგ is the
mirror on the forward side.  The counted noun never pluralises, so a count of
ninety-nine takes the same singular genitive as a count of one, and the
marker's POSITION is load-bearing -- put it in front, as every Germanic and
Romance locale does, and the phrase stops being Georgian.

Expected dates are computed here with ``timedelta``/``relativedelta``, never
read back from the extractor.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, nomatch, parse, start


@pytest.mark.parametrize("text,days", [
    ("ერთი დღის წინ", 1),
    ("ორი დღის წინ", 2),
    ("სამი დღის წინ", 3),
    ("ხუთი დღის წინ", 5),
    ("ათი დღის წინ", 10),
    ("თხუთმეტი დღის წინ", 15),
    ("ოცი დღის წინ", 20),
    ("ოცდაათი დღის წინ", 30),
    ("7 დღის წინ", 7),
])
def test_days_ago(text, days):
    assert start(text) == ad(ANCHOR - timedelta(days=days))


@pytest.mark.parametrize("text,days", [
    ("ორი დღის შემდეგ", 2),
    ("სამი დღის შემდეგ", 3),
    ("ცხრა დღის შემდეგ", 9),
    ("ოცდაერთი დღის შემდეგ", 21),
    ("4 დღის შემდეგ", 4),
])
def test_days_ahead(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,months", [
    ("სამი თვის წინ", 3),
    ("ერთი თვის წინ", 1),
    ("ექვსი თვის წინ", 6),
    ("თორმეტი თვის წინ", 12),
])
def test_months_ago(text, months):
    assert start(text) == ad(ANCHOR - relativedelta(months=months))


@pytest.mark.parametrize("text,months", [
    ("ორი თვის შემდეგ", 2),
    ("ხუთი თვის შემდეგ", 5),
])
def test_months_ahead(text, months):
    assert start(text) == ad(ANCHOR + relativedelta(months=months))


@pytest.mark.parametrize("text,years", [
    ("ორი წლის წინ", 2),
    ("ათი წლის წინ", 10),
    ("ორმოცი წლის წინ", 40),
])
def test_years_ago(text, years):
    """წელი syncopates its stem in the genitive -- წლის, not წელის -- and
    that is the form the postposition governs."""
    assert start(text) == ad(ANCHOR - relativedelta(years=years))


@pytest.mark.parametrize("text,hours", [
    ("ორი საათის წინ", -2),
    ("სამი საათის შემდეგ", 3),
])
def test_hours(text, hours):
    assert start(text) == ad(ANCHOR + timedelta(hours=hours))


@pytest.mark.parametrize("text,minutes", [
    ("ხუთი წუთის წინ", -5),
    ("ოცი წუთის შემდეგ", 20),
])
def test_minutes(text, minutes):
    assert start(text) == ad(ANCHOR + timedelta(minutes=minutes))


@pytest.mark.parametrize("text", ["თვის წინ", "წლის წინ", "დღის წინ"])
def test_bare_unit_is_a_single_step(text):
    """A genitive unit with no count is one of that unit, the same reading
    English gives "a month ago"."""
    r = parse(text)
    assert r is not None and r[1] == ""
    assert r[0].start < ad(ANCHOR)


@pytest.mark.parametrize("text", [
    "წინ სამი თვე", "შემდეგ ორი დღე", "წინ ორი წელი",
])
def test_preposed_marker_is_not_georgian(text):
    """წინ and შემდეგ are postpositions.  A preposed marker is the shape
    every Germanic and Romance locale uses, and reading it here would make
    the offset direction depend on a word order Georgian does not have."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "სამი თვე", "ორი დღე", "ათი წელი", "3 დღე",
])
def test_count_without_marker_is_not_a_time(text):
    """A bare count of units is a quantity, not a point in time."""
    nomatch(text)


@pytest.mark.parametrize("text,rel", [
    ("მომავალი თვე", relativedelta(months=1)),
    ("გასული თვე", relativedelta(months=-1)),
])
def test_relative_month(text, rel):
    """მომავალი and გასული are ADJECTIVES and stand before their noun --
    Georgian is postpositional in its adpositions, not in its modifiers."""
    target = (ANCHOR + rel).replace(day=1, hour=0, minute=0)
    assert start(text) == ad(target)


def test_this_month_is_the_current_calendar_month():
    assert start("ეს თვე") == ad(ANCHOR.replace(day=1, hour=0, minute=0))


@pytest.mark.parametrize("text,rel", [
    ("მომავალი წელი", relativedelta(years=1)),
    ("გასული წელი", relativedelta(years=-1)),
])
def test_relative_year(text, rel):
    target = (ANCHOR + rel).replace(month=1, day=1, hour=0, minute=0)
    assert start(text) == ad(target)
