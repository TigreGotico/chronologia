# -*- coding: utf-8 -*-
"""Nth-weekday-of-month for Czech: the LOCATIVE month-scope ("v <month-loc>")
and the bare GENITIVE month-scope ("<month-gen>").

Czech expresses "the Nth <weekday> of <month>" two ways.  The idiomatic form
uses the preposition ``v`` / ``ve`` ("v" = the locale's ``of`` connector) with
the month in the LOCATIVE case: "třetí pondělí v březnu 2020" (third Monday in
March).  The bare form drops the preposition and puts the month in the
GENITIVE: "třetí pondělí března 2020".  Both must bind ORD+WEEKDAY+MONTH and
resolve to the concrete date, not strand the weekday+month and read the
ordinal as a day-of-month.

Case forms: Internetová jazyková příručka (ÚJČ AV ČR), skloňování názvů
měsíců -- 6. pád (lokál) "v lednu ... v prosinci", 2. pád (genitiv) "ledna
... prosince".  Anchor 2017-06-27 (Tue); 3rd Monday of March 2020 is the
16th."""
from ._corpus import span, start_end, AstroDate


def test_third_monday_locative_v_march():
    # "třetí pondělí v březnu 2020" -- 3rd Monday of March 2020 = 16 Mar.
    s = span("třetí pondělí v březnu 2020")
    assert (s.start.year, s.start.month, s.start.day) == (2020, 3, 16)


def test_third_monday_bare_genitive_march():
    # "třetí pondělí března 2020" -- bare genitive month-scope, same date.
    s = span("třetí pondělí března 2020")
    assert (s.start.year, s.start.month, s.start.day) == (2020, 3, 16)


def test_first_monday_locative_january():
    # "první pondělí v lednu 2020" -- 1st Monday of Jan 2020 = 6 Jan.
    s = span("první pondělí v lednu 2020")
    assert (s.start.year, s.start.month, s.start.day) == (2020, 1, 6)


def test_second_friday_locative_ve_february():
    # "druhý pátek ve únoru 2020" -- ``ve`` allomorph; 2nd Fri Feb = 14 Feb.
    s = span("druhý pátek ve únoru 2020")
    assert (s.start.year, s.start.month, s.start.day) == (2020, 2, 14)


def test_bare_locative_month_still_a_month():
    # Regression: a bare "v březnu 2020" stays March 2020, not hijacked.
    st, en = start_end("v březnu 2020")
    assert st == AstroDate(2020, 3, 1)
    assert en == AstroDate(2020, 4, 1)
