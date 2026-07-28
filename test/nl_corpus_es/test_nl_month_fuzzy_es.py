# -*- coding: utf-8 -*-
"""Fuzzy edges of a NAMED month in Spanish: "a principios/mediados/finales de
marzo".

``principios``/``comienzos`` (early), ``mediados`` (mid) and ``finales`` (late)
carve the parent month into three equal arithmetic thirds -- the same rule the
engine applies to "principios de mes".  The subtlety is fractional boundaries:
a 31-day month splits at 10d8h/20d16h, a 28-day February at 9d8h/18d16h, so the
thirds do NOT land on midnight.  Gold is pure ``timedelta`` arithmetic over the
hand-derived parent edges; the parser never defines it.

A bare month resolves inside the anchor year (2017).  ``junio`` is covered
already by ``test_nl_scoped_seasons``; it is skipped here to avoid duplication.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end, nomatch


_MONTHS = [
    ("enero", 1), ("febrero", 2), ("marzo", 3), ("abril", 4),
    ("mayo", 5), ("julio", 7), ("agosto", 8), ("septiembre", 9),
    ("octubre", 10), ("noviembre", 11), ("diciembre", 12),
]
_PREFIX = [
    ("principios", "early"), ("comienzos", "early"),
    ("mediados", "mid"), ("finales", "late"),
]


def _third(s, e, part):
    w = (e - s) / 3
    edges = {
        "early": (s, s + w),
        "mid": (s + w, s + 2 * w),
        "late": (s + 2 * w, e),
    }[part]
    return AstroDate.from_datetime(edges[0]), AstroDate.from_datetime(edges[1])


def _cases():
    out = []
    for pw, part in _PREFIX:
        for mn, m in _MONTHS:
            ny, nm = (2017, m + 1) if m < 12 else (2018, 1)
            s = datetime(2017, m, 1)
            e = datetime(ny, nm, 1)
            want_s, want_e = _third(s, e, part)
            out.append((f"{pw} de {mn}", want_s, want_e))
    return out


@pytest.mark.parametrize("text,want_s,want_e", _cases())
def test_fuzzy_named_month(text, want_s, want_e):
    s, e = start_end(text)
    assert s == want_s, f"{text!r} start {s} != {want_s}"
    assert e == want_e, f"{text!r} end {e} != {want_e}"


@pytest.mark.parametrize("text", [
    "a principios",
    "un mes cualquiera",
])
def test_fuzzy_needs_a_period(text):
    nomatch(text)
