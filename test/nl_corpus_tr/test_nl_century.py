# -*- coding: utf-8 -*-
"""Century vocabulary -- "yuzyil" (TDK Guncel Turkce Sozluk: "yuz yillik
zaman parcasi", a hundred-year span).

Turkish is Ord-first ("Nth yuzyil"), inheriting the shared scoped_ordinal
base order unchanged.  Gold: the Nth century spans the 100 years opening in
year (N-1)*100 -- half-open, computed independently of the parser -- except
the first century, which (no year zero) spans [1, 101).

Decade is left unshipped for tr: "onyil" is a proposed calque, not a TDK
headword, and its bare compositional reading ("on yil" = "ten years")
already resolves through the ordinary NUM UNIT quantity path -- adding it
as a distinct "decade" noun would need a native speaker's call this corpus
does not make.
"""
import pytest

from ._corpus import parse, span, nomatch


@pytest.mark.parametrize("text,n", [
    ("birinci yüzyıl", 1), ("beşinci yüzyıl", 5),
    ("onuncu yüzyıl", 10), ("yirminci yüzyıl", 20),
])
def test_century_ordinal(text, n):
    s = span(text)
    assert s.start.year == (1 if n == 1 else (n - 1) * 100)
    assert s.end.year == (101 if n == 1 else n * 100)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["yüzyıl", "yüzyıllar"])
def test_bare_century_word_no_match(text):
    # a bare unit word carries no scope on its own -- it only binds inside
    # an ordinal or relative-offset construction.
    nomatch(text)


def test_compound_spelled_ordinal_refuses():
    # "on dokuzuncu" (ten + ninth) means "nineteenth", but the number fold
    # only reads spelled ordinals as single tokens: "dokuzuncu" folds to 9
    # alone, leaving "on" stranded beside it.  Composing multi-word spelled
    # ordinals is unsupported -- this refuses (None) rather than silently
    # answering "the 9th century" for "the nineteenth century".
    nomatch("on dokuzuncu yüzyıl")
