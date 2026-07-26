# -*- coding: utf-8 -*-
"""scoped_ordinal, re-enabled for Bulgarian via a connector-order override.

Bulgarian has no genitive case; "the Nth <weekday> of <month>" uses the
preposition "на" ("втори понеделник на март" -- lit. "second Monday of
March").  "на" is the locale's ``of`` connector, so the override ships the
connector orders "ORD WEEKDAY of MONTH" / "ORD UNIT of MONTH" -- NOT the bare
"ORD SCOPE_UNIT" that in #253 hijacked the year_ref reading of "NNNN
<year-noun>" ("през 1980 година").  Anchor 2017-06-27 (Tue); the 2nd Monday of
March 2017 is the 13th."""
from ._corpus import AstroDate, span, start_end


def test_second_monday_of_march():
    # "втори понеделник на март" -- 2nd Monday of March 2017.
    s = span("втори понеделник на март")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 3, 13)


def test_year_ref_not_hijacked():
    # #253 collision guard: "през 1980 година" must stay a YEAR.
    st, en = start_end("през 1980 година")
    assert st == AstroDate(1980, 1, 1)
    assert en == AstroDate(1981, 1, 1)
