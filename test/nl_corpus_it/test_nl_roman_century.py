"""Secoli in numeri romani -- la grafia consueta in italiano.

"secolo XII" (o il preposto "il XV secolo") è la forma scritta abituale.  Lega
solo accanto a un'unità di secolo/millennio; un omografo minuscolo non risolve.
Gold: il secolo N copre i 100 anni che aprono nell'anno gregoriano (N-1)*100.
"""
import pytest

from ._corpus import parse, span, nomatch


@pytest.mark.parametrize("text,y", [
    ("secolo XII", 1100), ("secolo XXI", 2000), ("secolo IV", 300),
    ("secolo XV", 1400), ("il XV secolo", 1400), ("III millennio", 2000),
])
def test_secolo_romano(text, y):
    assert span(text).start.year == y
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["mi piace", "vado via", "secolo"])
def test_omografi_non_legano(text):
    nomatch(text)
