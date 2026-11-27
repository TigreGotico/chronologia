# -*- coding: utf-8 -*-
"""scoped_ordinal, re-enabled for Croatian via a genitive-order override.

Croatian expresses "the Nth <weekday> of <month>" with a genitive month name
after the ordinal ("drugi ponedjeljak ožujka" -- lit. "second Monday of
March"), no connector word.  The override ships only the genitive
"ORD WEEKDAY MONTH" / "ORD UNIT MONTH" orders, NOT the bare "ORD SCOPE_UNIT"
that in #253 hijacked the year_ref reading of "NNNN <year-noun>" ("1980.
godine").  Anchor 2017-06-27 (Tue); the 2nd Monday of March is the 13th in 2017 but, with no year, March has ended at the
anchor and the month alone is March 2018 (ruling 1, changed 26 November 2026), so the 12th,
and the 3rd week of March 2018 starts the 19th."""
from ._corpus import AstroDate, span, start_end


def test_second_monday_of_march():
    # "drugi ponedjeljak ožujka" -- 2nd Monday of March 2018 (ruling 1: March has ended at the anchor).
    s = span("drugi ponedjeljak ožujka")
    assert (s.start.year, s.start.month, s.start.day) == (2018, 3, 12)


def test_third_week_of_march():
    # "treći tjedan ožujka" -- 3rd week of March 2018 (Monday-aligned; ruling 1).
    s = span("treći tjedan ožujka")
    assert (s.start.year, s.start.month, s.start.day) == (2018, 3, 19)


def test_year_ref_not_hijacked():
    # #253 collision guard: "1980. godine" must stay a YEAR.
    st, en = start_end("1980. godine")
    assert st == AstroDate(1980, 1, 1)
    assert en == AstroDate(1981, 1, 1)
