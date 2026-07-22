"""Wave 1 -- eras and deep time.

BC/BCE map to astronomical year numbering (44 BC == year -43, i.e. 1 - n);
AD/CE map to the year itself; "N BP" / "N years before present" count back
from 1950 (year 1950 - n).  Numeric deep time ("66 million years ago")
goes through the radiocarbon before-present convention, so the start year
is ``1950 - N*scale``.  Named geological periods come straight from the ICS
chart via chronologia; "early/mid/late" subdivide them.
"""
import pytest

import chronologia as _c

from ._corpus import ANCHOR, AstroDate, start, start_end, span, nomatch


# -- BC / BCE (year -> 1 - n) ---------------------------------------------

@pytest.mark.parametrize("text,n", [
    ("44 bc", 44), ("44 bce", 44), ("300 bce", 300), ("753 bc", 753),
    ("10000 bc", 10000), ("1 bc", 1), ("336 bc", 336), ("509 bc", 509),
    ("2500 bce", 2500), ("79 bc", 79), ("323 bc", 323), ("146 bc", 146),
    ("55 bc", 55), ("218 bce", 218), ("480 bc", 480), ("31 bc", 31),
    ("1200 bce", 1200), ("3000 bc", 3000),
])
def test_bc(text, n):
    assert start(text) == AstroDate(1 - n, 1, 1)
    assert span(text).width.days >= 365


# -- AD / CE (year -> n) --------------------------------------------------

@pytest.mark.parametrize("text,n", [
    ("1492 ad", 1492), ("800 ce", 800), ("ad 44", 44), ("79 ad", 79),
    ("476 ad", 476), ("1066 ad", 1066), ("2000 ce", 2000), ("1 ad", 1),
    ("1969 ce", 1969), ("ad 800", 800),
])
def test_ad(text, n):
    assert start(text) == AstroDate(n, 1, 1)


# -- before present (year -> 1950 - n) ------------------------------------

@pytest.mark.parametrize("text,n", [
    ("2000 bp", 2000), ("2000 years before present", 2000),
    ("5000 bp", 5000), ("500 bp", 500),
    ("12000 years before present", 12000),
])
def test_before_present(text, n):
    assert start(text) == AstroDate(1950 - n, 1, 1)


# -- numeric deep time (year -> 1950 - N*scale) ---------------------------

@pytest.mark.parametrize("text,val", [
    ("66 million years ago", 66_000_000),
    ("4.5 billion years ago", 4_500_000_000),
    ("2 million years ago", 2_000_000),
    ("540 million years ago", 540_000_000),
    ("13.8 billion years ago", 13_800_000_000),
    ("10 thousand years ago", 10_000),
    ("250 million years ago", 250_000_000),
    ("3 billion years ago", 3_000_000_000),
    ("66 million years before present", 66_000_000),
])
def test_deep_time(text, val):
    assert start(text).year == 1950 - val


# -- deep-time referential WIDTH (sig-figs of the SPOKEN value) ------------
# "66 million" is precise to the million (one significant place of "66"), so
# the honest span is 1 million years wide -- NOT 1 year.  A decimal digit
# tightens it: "66.5 million" -> 100 ka, "4.5 billion" -> 100 Ma.  Width is
# read at the spoken unit, before value x scale collapses to a year count.
@pytest.mark.parametrize("text,width_years", [
    ("66 million years ago", 1_000_000),
    ("2 million years ago", 1_000_000),
    ("540 million years ago", 1_000_000),
    ("250 million years ago", 1_000_000),
    ("3 billion years ago", 1_000_000_000),
    ("10 thousand years ago", 1_000),
    ("66.5 million years ago", 100_000),
    ("4.5 billion years ago", 100_000_000),
    ("13.8 billion years ago", 100_000_000),
    ("66 million years before present", 1_000_000),
])
def test_deep_time_width(text, width_years):
    s, e = start_end(text)
    assert e.year - s.year == width_years


# -- named geological periods (from the ICS chart) ------------------------

@pytest.mark.parametrize("text,key", [
    ("during the jurassic", "jurassic"),
    ("the cretaceous", "cretaceous"),
    ("in the triassic", "triassic"),
    ("the permian", "permian"),
    ("the holocene", "holocene"),
    ("the pleistocene", "pleistocene"),
    ("the cambrian", "cambrian"),
    ("during the mesozoic", "mesozoic"),
    ("the cenozoic", "cenozoic"),
    ("in the neolithic", "neolithic_gb"),
    ("the carboniferous", "carboniferous"),
    ("the devonian", "devonian"),
    ("the silurian", "silurian"),
    ("the ordovician", "ordovician"),
    ("during the paleozoic", "paleozoic"),
    ("the miocene", "miocene"),
    ("the eocene", "eocene"),
    ("the oligocene", "oligocene"),
    ("the paleocene", "paleocene"),
    ("the quaternary", "quaternary"),
    ("the neogene", "neogene"),
    ("the paleogene", "paleogene"),
])
def test_named_period(text, key):
    s, e = start_end(text)
    p = _c.PERIODS[key].span
    assert s == p.start and e == p.end


# -- early / mid / late subdivide -----------------------------------------

@pytest.mark.parametrize("text,key,part", [
    ("the late cretaceous", "cretaceous", "late"),
    ("the early triassic", "triassic", "early"),
    ("mid jurassic", "jurassic", "mid"),
    ("the early jurassic", "jurassic", "early"),
    ("the late permian", "permian", "late"),
    ("the middle jurassic", "jurassic", "mid"),
])
def test_period_subdivide(text, key, part):
    s, e = start_end(text)
    sub = _c.subdivide(_c.PERIODS[key], part)
    assert s == sub.start and e == sub.end


# -- deferred phrasings ---------------------------------------------------

@pytest.mark.parametrize("text,key", [
    ("in the bronze age", "bronze_age_gb"),
    ("the bronze age", "bronze_age_gb"),
    ("the iron age", "iron_age_gb"),
])
def test_bronze_age(text, key):
    s, e = start_end(text)
    p = _c.PERIODS[key].span
    assert s == p.start and e == p.end


@pytest.mark.xfail(reason="no citable single-span 'stone age'/'middle ages' "
                          "in chronologia PERIODS (neolithic != stone age; "
                          "medieval span needs a sourced entry) -- would "
                          "require inventing a boundary", strict=True)
def test_stone_age():
    start_end("the stone age")


@pytest.mark.parametrize("text,year", [
    ("the year twelve thousand", 12000),
    ("the year two thousand", 2000),
    ("year ten thousand", 10000),
])
def test_spelled_year(text, year):
    assert start(text) == AstroDate(year, 1, 1)


def test_bare_year_word():
    assert start("the year 12000") == AstroDate(12000, 1, 1)
