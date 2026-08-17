# -*- coding: utf-8 -*-
"""A bare cardinal before a plural "decades"/"centuries" unit refuses,
matching the sibling duration units ("two weeks", "two years") that already
refuse the same shape.

The number fold collapses a spelled cardinal ("two") and a spelled ordinal
("second") to the identical numeric token, so a plural scope noun is the
only surviving signal that "two centuries" names a COUNT, not the ordinal
era index "the 2nd century" happens to share a folded token with. Reading
a bare cardinal here as an era index silently produced an ancient date
nobody asked for ("two decades" -> the 2nd decade of the common era,
0010-01-01..0020-01-01).

Genuine ordinal phrasings (spelled, digit, "-th") and offset phrasings
("... ago", "in ...") are unaffected -- they bind through different slots
(a real ORD with a SINGULAR scope noun, or ``relative_offset``'s UNIT slot)
and are pinned here as controls so this fix cannot regress them.
"""
from datetime import datetime

from ._corpus import AstroDate, nomatch, span, start_end

ANCHOR = datetime(2026, 8, 14, 10, 0)


# -- the defect: bare cardinal + plural decade/century unit refuses --------

def test_bare_cardinal_decade_refuses():
    nomatch('two decades', anchor=ANCHOR)


def test_bare_cardinal_century_refuses():
    nomatch('two centuries', anchor=ANCHOR)


def test_bare_digit_cardinal_decade_refuses():
    nomatch('2 decades', anchor=ANCHOR)


def test_bare_digit_cardinal_century_refuses():
    nomatch('2 centuries', anchor=ANCHOR)


# -- the sibling units already refuse this shape (the inconsistency that
# makes the above a defect rather than a convention) -----------------------

def test_bare_cardinal_weeks_refuses():
    nomatch('two weeks', anchor=ANCHOR)


def test_bare_cardinal_years_refuses():
    nomatch('two years', anchor=ANCHOR)


# -- controls: genuine ordinal phrasings keep working -----------------------

def test_the_second_decade():
    s, e = start_end('the second decade', anchor=ANCHOR)
    assert s == AstroDate(10, 1, 1)
    assert e == AstroDate(20, 1, 1)


def test_the_2nd_century():
    s, e = start_end('the 2nd century', anchor=ANCHOR)
    assert s == AstroDate(100, 1, 1)
    assert e == AstroDate(200, 1, 1)


def test_the_twentieth_century():
    s, e = start_end('the twentieth century', anchor=ANCHOR)
    assert s == AstroDate(1900, 1, 1)
    assert e == AstroDate(2000, 1, 1)


def test_the_1920s():
    s, e = start_end('the 1920s', anchor=ANCHOR)
    assert s == AstroDate(1920, 1, 1)
    assert e == AstroDate(1930, 1, 1)


# -- controls: offset phrasings keep working (different construction) ------

def test_two_centuries_ago():
    s, e = start_end('two centuries ago', anchor=ANCHOR)
    assert s == AstroDate(1826, 8, 14, 10, 0)
    assert e == AstroDate(1926, 8, 14, 10, 0)


def test_in_two_decades():
    s, e = start_end('in two decades', anchor=ANCHOR)
    assert s == AstroDate(2046, 8, 14, 10, 0)
    assert e == AstroDate(2056, 8, 14, 10, 0)


# -- controls: neighbouring decade-span readings keep working --------------

def test_the_1990s():
    s, e = start_end('the 1990s', anchor=ANCHOR)
    assert s == AstroDate(1990, 1, 1)
    assert e == AstroDate(2000, 1, 1)


def test_the_early_2000s():
    s, e = start_end('the early 2000s', anchor=ANCHOR)
    assert s == AstroDate(2000, 1, 1)
    assert e == AstroDate(2003, 1, 1)


def test_deep_time_unaffected():
    s, e = start_end('66 million years ago', anchor=ANCHOR)
    assert s == AstroDate(-65998050, 1, 1)
    assert e == AstroDate(-64998050, 1, 1)
