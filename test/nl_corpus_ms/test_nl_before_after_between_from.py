# -*- coding: utf-8 -*-
"""Malay "sebelum"/"selepas" (before/after), "antara ... dan ..." (between)
and "dari"/"daripada" (range from-lead) were undeclared: each marker fell
through to the bare-endpoint reading and was left stranded in the remainder
("selepas Januari" -> January itself, remainder "selepas"), silently
dropping the very word that reverses the meaning (before/after/between).

"sebelum X" now binds the open-range reading ``[now, X's end)`` when X is in
the future, and is refused (no match) when X's end is not in the future --
mirroring Spanish "antes de X"/English "before X" exactly (see
``test_es_r146_before_after_holiday.py``). "selepas X" ("after X") is the open span from the end of X
onward, a :class:`DateSpan` with ``open_end``. "antara
A dan B" binds the closed range [A, B). "dari A hingga B" / "daripada A
hingga B" consume their own from-lead.

Expected values are independently hand-computed against the anchor.
"""
from datetime import datetime

from chronologia.astrodate import AstroDate
from chronologia.extract import extract_timespan

from ._corpus import ANCHOR, nomatch, start_end

LANG = "ms"


def _result(text, anchor=ANCHOR):
    return extract_timespan(text, LANG, anchor)


def test_sebelum_future_year_binds_open_range():
    r = _result("sebelum 2030")
    assert r is not None
    assert r[0].start == AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day,
                                   ANCHOR.hour, ANCHOR.minute)
    # ruling 29: "before X" ends where X starts
    assert r[0].end == AstroDate(2030, 1, 1)
    assert r.remainder == ""


def test_sebelum_past_year_refused():
    nomatch("sebelum 2020")


def test_selepas_year_is_open_from_its_end():
    r = _result("selepas 2030")
    assert (r[0].start, r[0].open_end, r.remainder) == (AstroDate(2031, 1, 1), True, "")


def test_selepas_month_is_open_from_its_end():
    # the next January after 15 July 2026 is January 2027
    r = _result("selepas Januari")
    assert (r[0].start, r[0].open_end, r.remainder) == (AstroDate(2027, 2, 1), True, "")


def test_antara_dan_binds_closed_range():
    ss, ee = start_end("antara 2010 dan 2020")
    assert ss == AstroDate(2010, 1, 1) and ee == AstroDate(2021, 1, 1)


def test_antara_dan_empty_remainder():
    r = _result("antara 2010 dan 2020")
    assert r is not None
    assert r.remainder == ""


def test_dari_hingga_consumes_lead():
    r = _result("dari Januari hingga Mac")
    assert r is not None
    assert r[0].start == AstroDate(2027, 1, 1)
    assert r[0].end == AstroDate(2027, 4, 1)
    assert r.remainder == ""


def test_daripada_hingga_consumes_lead():
    r = _result("daripada Januari hingga Mac")
    assert r is not None
    assert r[0].start == AstroDate(2027, 1, 1)
    assert r[0].end == AstroDate(2027, 4, 1)
    assert r.remainder == ""


def test_bare_antara_never_raises():
    from ._corpus import parse
    parse("antara")
