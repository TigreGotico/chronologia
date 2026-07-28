# -*- coding: utf-8 -*-
"""More French date ranges (fr): "du A au B", "entre le A et le B", month
ranges, all within a single prefer-future year so both endpoints agree.

A closed "du A au B" day range is inclusive of B, so the exclusive end is
B + 1 day; a month range "de M1 à M2" runs to the first of the month after M2.
Endpoints with no year take the prefer-future year off the anchor day
(2017-06-27): a fully-past window rolls to 2018.

(KNOWN DEFECT, not asserted: a single trailing year on a range binds only the
right endpoint -- "de janvier à mars 2020" yields 2017-01 .. 2020-04, and the
same happens in English "from January to March 2020".  Only unambiguous
single-year windows are pinned here.)

Every edge below is hand-derived.  Anchor Tuesday 2017-06-27 13:04.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end


# day ranges: (text, start Y-M-D, end Y-M-D)  -- end already exclusive (B+1)
_DAY = [
    ("du 3 au 7 juillet", (2017, 7, 3), (2017, 7, 8)),
    ("du 2 au 9 juillet", (2017, 7, 2), (2017, 7, 10)),
    ("du 14 au 21 juillet", (2017, 7, 14), (2017, 7, 22)),
    ("du 1er au 31 juillet", (2017, 7, 1), (2017, 8, 1)),
    ("du 22 au 29 août", (2017, 8, 22), (2017, 8, 30)),
    ("du 1er au 15 août", (2017, 8, 1), (2017, 8, 16)),
    ("du 5 au 8 septembre", (2017, 9, 5), (2017, 9, 9)),
    ("du 20 septembre au 5 octobre", (2017, 9, 20), (2017, 10, 6)),
    ("du 10 au 20 octobre", (2017, 10, 10), (2017, 10, 21)),
    ("du 15 au 20 novembre", (2017, 11, 15), (2017, 11, 21)),
    ("du 1er au 7 décembre", (2017, 12, 1), (2017, 12, 8)),
    ("du 10 au 25 décembre", (2017, 12, 10), (2017, 12, 26)),
    ("du 24 au 31 décembre", (2017, 12, 24), (2018, 1, 1)),
    ("du 28 février au 3 mars", (2018, 2, 28), (2018, 3, 4)),   # both past -> 2018
    ("entre le 5 et le 12 août", (2017, 8, 5), (2017, 8, 13)),
    ("entre le 3 et le 7 novembre", (2017, 11, 3), (2017, 11, 8)),
]


@pytest.mark.parametrize("text,s,e", _DAY)
def test_day_range(text, s, e):
    got = start_end(text)
    assert got == (AstroDate(*s), AstroDate(*e)), f"{text!r} -> {got}"


# month ranges: end = first of the month after the right month
_MONTH = [
    ("entre mars et juin", (2017, 3, 1), (2017, 7, 1)),
    ("de septembre à décembre", (2017, 9, 1), (2018, 1, 1)),
    ("de juin à août", (2017, 6, 1), (2017, 9, 1)),
]


@pytest.mark.parametrize("text,s,e", _MONTH)
def test_month_range(text, s, e):
    got = start_end(text)
    assert got == (AstroDate(*s), AstroDate(*e)), f"{text!r} -> {got}"
