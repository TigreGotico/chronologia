"""Séculos em numeração romana -- a grafia corrente em português.

"século XII" é a forma escrita habitual.  Só liga junto de uma unidade de
século/milénio; um homógrafo minúsculo ("vi o filme" = "I saw the film")
nunca resolve.  Gold: o século N abrange os 100 anos que abrem no ano
gregoriano (N-1)*100.
"""
import pytest

from ._corpus import parse, span, nomatch


@pytest.mark.parametrize("text,y", [
    ("século XII", 1100), ("século XXI", 2000), ("século IV", 300),
    ("século XV", 1400), ("o século XV", 1400), ("milénio III", 2000),
])
def test_seculo_romano(text, y):
    assert span(text).start.year == y
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["vi o filme", "mix de tudo", "século"])
def test_confusaveis_nao_ligam(text):
    nomatch(text)
