# -*- coding: utf-8 -*-
"""Day + daypart composition in Spanish: "el viernes por la tarde", "ayer por
la noche", "mañana por la mañana".

A day reference (a weekday, or a relative day like ``hoy``/``ayer``/``mañana``)
composes with a CLDR ``es`` day-period band via ``por la``: ``la mañana``
``[06:00, 12:00)``, ``la tarde`` ``[12:00, 20:00)``, ``la noche``
``[20:00, 24:00)``.  The span is that band placed on the resolved day.

Gold is independent: the weekday oracle takes the next occurrence STRICTLY
after the anchor date (2017-06-27, Tuesday); the band hours come from the CLDR
table transcribed in :mod:`chronologia.dayparts`.  The parser never defines
either.  ``pasado mañana``/``anteayer`` compounds are handled separately and
some are on the BUG list; only the verified-clean compositions are asserted.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import parse, span


_BANDS = {
    "la mañana": (6, 12),
    "la tarde": (12, 20),
    "la noche": (20, 24),
}
_WD = {
    "lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3,
    "viernes": 4, "sábado": 5, "domingo": 6,
}
_REL = {
    "hoy": date(2017, 6, 27),
    "ayer": date(2017, 6, 26),
    "anteayer": date(2017, 6, 25),
    "mañana": date(2017, 6, 28),
}


def _band_span(d, lo, hi):
    s = datetime(d.year, d.month, d.day, lo, 0)
    if hi == 24:
        e = datetime(d.year, d.month, d.day) + timedelta(days=1)
    else:
        e = datetime(d.year, d.month, d.day, hi, 0)
    return AstroDate.from_datetime(s), AstroDate.from_datetime(e)


def _next_wd(wd):
    base = date(2017, 6, 27)
    ahead = (wd - base.weekday()) % 7 or 7
    return base + timedelta(days=ahead)


def _cases():
    out = []
    for wn, wd in _WD.items():
        for bn, (lo, hi) in _BANDS.items():
            s, e = _band_span(_next_wd(wd), lo, hi)
            out.append((f"el {wn} por {bn}", s, e))
    for rn, d in _REL.items():
        for bn, (lo, hi) in _BANDS.items():
            s, e = _band_span(d, lo, hi)
            out.append((f"{rn} por {bn}", s, e))
    return out


@pytest.mark.parametrize("text,want_s,want_e", _cases())
def test_day_plus_daypart(text, want_s, want_e):
    s = span(text)
    assert (s.start, s.end) == (want_s, want_e), f"{text!r} -> {s}"


@pytest.mark.parametrize("text", [
    "el lunes por la mañana",
    "buenas noches",
    "por la tarde",
])
def test_daypart_never_raises(text):
    parse(text)
