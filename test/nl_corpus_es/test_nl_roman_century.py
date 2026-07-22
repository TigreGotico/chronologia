"""Siglos en numeración romana -- la grafía habitual en español.

"siglo XII" es la forma escrita corriente.  Solo liga junto a una unidad de
siglo/milenio; un homógrafo en minúscula ("vi la película") nunca resuelve.
Gold: el siglo N abarca los 100 años que abren en el año gregoriano (N-1)*100.
"""
import pytest

from ._corpus import parse, span, nomatch


@pytest.mark.parametrize("text,y", [
    ("siglo XII", 1100), ("siglo XXI", 2000), ("siglo IV", 300),
    ("siglo XV", 1400), ("el siglo XV", 1400), ("milenio III", 2000),
])
def test_siglo_romano(text, y):
    assert span(text).start.year == y
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["vi la película", "plan C", "siglo"])
def test_confusables_no_ligan(text):
    nomatch(text)
