# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: Spanish clock idioms across the FULL hour matrix
(1-12) -- "y cuarto"/"y media"/"menos cuarto"/"en punto" and the
mañana/tarde/noche meridiem qualifiers -- rather than the handful of spot
hours ``test_nl_clock.py`` already pins.

Gold is minute-wide spans, prefer-future rolled exactly as the shared
``clk()`` oracle in ``test_nl_clock.py`` computes it (duplicated here so this
file stands alone): the literal hour/minute is placed on the anchor's civil
day, then bumped a day forward if that clock-time has already passed.

"las doce de la noche" is a genuinely ambiguous idiom (midnight vs. the
literal noon-style hour-12 reading) and is dropped rather than asserted
either way -- see the campaign notes for the ``doce`` + ``noche`` exclusion.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start

_NUM = [
    ("una", 1), ("dos", 2), ("tres", 3), ("cuatro", 4), ("cinco", 5),
    ("seis", 6), ("siete", 7), ("ocho", 8), ("nueve", 9), ("diez", 10),
    ("once", 11), ("doce", 12),
]

# exact strings already pinned by test_nl_clock.py -- skip to avoid dupes.
_ALREADY_COVERED = {
    ("cuarto", 3), ("cuarto", 9), ("media", 3), ("media", 9),
    ("menos_cuarto", 2),
    ("manana", 9), ("tarde", 3),
}


def clk(h, mi, s=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


def _fraction_cases():
    out = []
    for nw, h in _NUM:
        if ("cuarto", h) not in _ALREADY_COVERED:
            out.append((f"las {nw} y cuarto", clk(h, 15)))
        if ("media", h) not in _ALREADY_COVERED:
            out.append((f"las {nw} y media", clk(h, 30)))
    return out


def _menos_cuarto_cases():
    out = []
    for nw, h in _NUM:
        if ("menos_cuarto", h) in _ALREADY_COVERED:
            continue
        out.append((f"las {nw} menos cuarto", clk(h - 1, 45)))
    return out


def _en_punto_cases():
    return [(f"las {nw} en punto", clk(h, 0)) for nw, h in _NUM]


def _manana_cases():
    out = []
    for nw, h in _NUM:
        if ("manana", h) in _ALREADY_COVERED:
            continue
        out.append((f"las {nw} de la mañana", clk(0 if h == 12 else h, 0)))
    return out


def _tarde_cases():
    out = []
    for nw, h in _NUM:
        if ("tarde", h) in _ALREADY_COVERED:
            continue
        out.append((f"las {nw} de la tarde", clk(h if h == 12 else h + 12, 0)))
    return out


def _noche_cases():
    # "de la noche" is a midnight-crossing BAND, not a uniform +12 PM shift:
    # the small hours 1..5 stay AM ("la una de la noche" == 01:00) and the
    # evening hours 6..11 are PM ("las diez de la noche" == 22:00).  AM ceiling
    # follows the es madrugada band [00:00, 06:00); RAE/DPD s.v. "noche".
    # doce excluded: "las doce de la noche" is an ambiguous idiom, dropped.
    out = []
    for nw, h in _NUM:
        if h == 12:
            continue
        out.append((f"las {nw} de la noche", clk(h if h <= 5 else h + 12, 0)))
    return out


@pytest.mark.parametrize("text,g", _fraction_cases())
def test_hour_fraction_matrix(text, g):
    assert start(text) == g, text


@pytest.mark.parametrize("text,g", _menos_cuarto_cases())
def test_menos_cuarto_matrix(text, g):
    assert start(text) == g, text


@pytest.mark.parametrize("text,g", _en_punto_cases())
def test_en_punto_matrix(text, g):
    assert start(text) == g, text


@pytest.mark.parametrize("text,g", _manana_cases())
def test_manana_matrix(text, g):
    assert start(text) == g, text


@pytest.mark.parametrize("text,g", _tarde_cases())
def test_tarde_matrix(text, g):
    assert start(text) == g, text


@pytest.mark.parametrize("text,g", _noche_cases())
def test_noche_matrix(text, g):
    assert start(text) == g, text
