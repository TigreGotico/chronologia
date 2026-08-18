# -*- coding: utf-8 -*-
"""Indonesian "sebelum"/"sesudah"/"setelah" (before/after), "antara ... dan
..." (between) and "dari" (range from-lead) were undeclared: each marker fell
through to the bare-endpoint reading and was left stranded in the remainder
("sebelum 2020" -> the year 2020 itself, remainder "sebelum"), silently
dropping the very word that reverses the meaning (before/after/between).

"sebelum X" now binds the open-range reading ``[now, X's end)`` when X is in
the future, and is refused (no match) when X's end is not in the future --
mirroring Spanish "antes de X"/English "before X" exactly (see
``test_es_r146_before_after_holiday.py``). "sesudah"/"setelah X" ("after X")
is always refused: :class:`DateSpan` has no open-ended-future representation.
"antara A dan B" binds the closed range [A, B). "dari A sampai/hingga B"
consumes its own "dari" lead.

Expected values are independently hand-computed against the anchor.
"""
from datetime import datetime

from chronologia.astrodate import AstroDate
from chronologia.extract import extract_timespan

from ._corpus import ANCHOR, nomatch, start_end

LANG = "id"


def _result(text, anchor=ANCHOR):
    return extract_timespan(text, LANG, anchor)


def test_sebelum_future_year_binds_open_range():
    r = _result("sebelum 2030")
    assert r is not None
    assert r[0].start == AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day,
                                   ANCHOR.hour, ANCHOR.minute)
    assert r[0].end == AstroDate(2031, 1, 1)
    assert r.remainder == ""


def test_sebelum_past_year_refused():
    nomatch("sebelum 2020")


def test_sesudah_refused_not_stranded():
    nomatch("sesudah 2030")


def test_setelah_refused_not_stranded():
    nomatch("setelah Januari")


def test_antara_dan_binds_closed_range():
    ss, ee = start_end("antara 2010 dan 2020")
    assert ss == AstroDate(2010, 1, 1) and ee == AstroDate(2021, 1, 1)


def test_antara_dan_empty_remainder():
    r = _result("antara 2010 dan 2020")
    assert r is not None
    assert r.remainder == ""


def test_dari_sampai_consumes_lead():
    r = _result("dari Januari sampai Maret")
    assert r is not None
    assert r[0].start == AstroDate(2026, 1, 1)
    assert r[0].end == AstroDate(2026, 4, 1)
    assert r.remainder == ""


def test_bare_antara_never_raises():
    from ._corpus import parse
    parse("antara")
