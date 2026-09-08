"""Catalan future offsets with "d'aquí a", and the clock hour closed by
"hores".

"d'aquí a" is a preposition meaning "in, within (a time span)": Wiktionary
(en), d'aquí a; ca.wikipedia "Guzaarish": "començar a rodar d'aquí a cinc
dies".  The noun closes a spoken hour the way Portuguese "horas" does:
ca.wikipedia "Teatre Nacional de l'Opéra-Comique" ("a les 21 hores, un segon
incendi"), "Normand L'Amour" ("La fi del món és a les set hores").

Anchor: Tuesday 2017-06-27 13:04.  An offset keeps the anchor's time of day;
a clock names its next occurrence.  Every value is anchor arithmetic.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


def _offset(text, delta, grain, rem=""):
    res = parse(text)
    assert res is not None, f"{text!r} did not parse"
    assert res.remainder == rem, f"{text!r} left {res.remainder!r}"
    assert res[0].start == ad(ANCHOR + delta)
    assert res[0].end == ad(ANCHOR + delta + grain)


D, H = timedelta(days=1), timedelta(hours=1)


@pytest.mark.parametrize("text,delta,grain,rem", [
    ("d'aquí a 5 dies", 5 * D, D, ""),
    ("d'aquí a 2 setmanes", 14 * D, 7 * D, ""),
    ("d'aquí a 90 minuts", timedelta(minutes=90), timedelta(minutes=1), ""),
    ("d'aquí a una hora", H, H, ""),
    ("envia felicitacions d'aquí a 5 anys", None, None, "envia felicitacions"),
    ("truca'm per a quedar d'aquí a 8 setmanes i 2 dies", 58 * D, D,
     "truca'm per a quedar"),
])
def test_daqui_a_offset(text, delta, grain, rem):
    if delta is None:
        res = parse(text)
        assert res is not None and res.remainder == rem
        assert res[0].start.year == ANCHOR.year + 5
        assert (res[0].start.month, res[0].start.day) == (ANCHOR.month, ANCHOR.day)
        return
    _offset(text, delta, grain, rem)


def test_daqui_a_and_dins_de_agree():
    assert parse("d'aquí a 5 dies")[0] == parse("dins de 5 dies")[0]


def _next(h):
    cand = ANCHOR.replace(hour=h, minute=0, second=0)
    if cand <= ANCHOR:
        cand += D
    return ad(cand)


@pytest.mark.parametrize("text,h", [
    ("a les 7 hores", 7),
    ("a les set hores", 7),
    ("a les 21 hores", 21),
    ("les 7 hores", 7),
])
def test_hores_closes_the_hour(text, h):
    res = parse(text)
    assert res is not None and res.remainder == "", f"{text!r} -> {res}"
    assert res[0].start == _next(h)
    assert res[0].end == _next(h) + timedelta(minutes=1)
