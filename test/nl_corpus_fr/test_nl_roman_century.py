"""Siècles en chiffres romains -- la graphie usuelle en français.

"XIIe siècle" (l'ordinal en exposant précède l'unité) est la forme écrite
habituelle.  Ne lie qu'à côté d'une unité de siècle/millénaire ; un homographe
minuscule ("dix ans", "six chats") ne résout jamais.  Gold : le siècle N couvre
les 100 ans ouvrant l'année grégorienne (N-1)*100.
"""
import pytest

from ._corpus import parse, span, nomatch


@pytest.mark.parametrize("text,y", [
    ("XIIe siècle", 1100), ("le XXIe siècle", 2000), ("IVe siècle", 300),
    ("XVe siècle", 1400), ("IIIe millénaire", 2000),
])
def test_siecle_romain(text, y):
    assert span(text).start.year == y
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["dix ans", "six chats", "siècle"])
def test_homographes_ne_lient_pas(text):
    nomatch(text)
