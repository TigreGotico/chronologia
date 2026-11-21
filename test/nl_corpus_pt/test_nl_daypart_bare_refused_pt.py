# -*- coding: utf-8 -*-
"""Portuguese reads a bare day-part word only when it is the whole text.

The slot holds every day-part surface the locale ships, so a bare order that
admitted "manhã" would also admit "tarde", which is equally the adverb *late*:
"mais tarde", "cheguei tarde" and "é tarde demais" name no time.  The bare
order therefore fires only when the day-part word is the entire text
(``marker_daypart_alone.voc``, ruling 28).  Inside a sentence the bare word
reads nothing.

What Portuguese says inside a sentence is framed, and every frame resolves:
"de manhã", "pela manhã", "a manhã", "esta manhã".

Gold bands are the pt row of the CLDR table transcribed in
:mod:`chronologia.dayparts` -- madrugada ``[00:00, 06:00)``, manhã
``[06:00, 12:00)``, tarde ``[12:00, 19:00)``, noite ``[19:00, 24:00)`` -- on
the anchor's own day, 2017-06-27.
"""
import pytest

from ._corpus import AstroDate, nomatch, parse


@pytest.mark.parametrize("text", [
    "mais tarde", "cheguei tarde", "é tarde demais", "boa noite",
    "manhã fria", "noite fria", "tarde demais",
])
def test_bare_daypart_word_in_a_sentence_is_not_a_span(text):
    nomatch(text)


@pytest.mark.parametrize("text,lo,hi", [
    ("de manhã", 6, 12),
    ("pela manhã", 6, 12),
    ("a manhã", 6, 12),
    ("esta manhã", 6, 12),
    ("à tarde", 12, 19),
    ("pela tarde", 12, 19),
    ("pela noite", 19, 24),
    ("esta noite", 19, 24),
    ("de madrugada", 0, 6),
    ("pela madrugada", 0, 6),
])
def test_the_framed_form_resolves(text, lo, hi):
    r = parse(text)
    assert r is not None, text
    end = (AstroDate(2017, 6, 28, 0, 0, 0) if hi == 24
           else AstroDate(2017, 6, 27, hi, 0, 0))
    assert (r.span.start, r.span.end) == (AstroDate(2017, 6, 27, lo, 0, 0), end)
    assert r.remainder == "", f"{text!r} stranded {r.remainder!r}"


@pytest.mark.parametrize("text,lo,hi", [
    ("manhã", 6, 12),
    ("tarde", 12, 19),
    ("noite", 19, 24),
    ("madrugada", 0, 6),
])
def test_a_day_part_word_alone_is_its_band(text, lo, hi):
    r = parse(text)
    assert r is not None, text
    end = (AstroDate(2017, 6, 28, 0, 0, 0) if hi == 24
           else AstroDate(2017, 6, 27, hi, 0, 0))
    assert (r.span.start, r.span.end) == (AstroDate(2017, 6, 27, lo, 0, 0), end)
    assert r.remainder == "", f"{text!r} stranded {r.remainder!r}"
