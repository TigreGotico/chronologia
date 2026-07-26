# -*- coding: utf-8 -*-
"""scoped_ordinal, re-enabled for Russian via a genitive-order override.

Russian expresses "the Nth <weekday> of <month>" with a plain genitive month
name after the ordinal ("второй понедельник марта" -- lit. "second Monday of
March"), no connector word.  The base ``scoped_ordinal`` was disabled in #253
because its bare "ORD SCOPE_UNIT" order hijacked the year_ref reading of
"NNNN <year-noun>" ("в 1980 году"); the override ships only the genitive
"ORD WEEKDAY MONTH" / "ORD UNIT MONTH" orders, so the year_ref reading stays
intact.  Anchor 2017-06-27 (Tue); the 2nd Monday of March 2017 is the 13th."""
from ._corpus import AstroDate, span, start_end


def test_second_monday_of_march():
    # "второй понедельник марта" -- 2nd Monday of March 2017.
    s = span("второй понедельник марта")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 3, 13)


def test_year_ref_not_hijacked():
    # the whole reason for the #253 disable: "в 1980 году" must stay a YEAR,
    # not fold "1980" to an ordinal over the "году" scope-unit.
    st, en = start_end("в 1980 году")
    assert st == AstroDate(1980, 1, 1)
    assert en == AstroDate(1981, 1, 1)
