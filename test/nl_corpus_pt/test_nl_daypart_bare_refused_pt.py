# -*- coding: utf-8 -*-
"""Portuguese never reads a bare day-part word as a span, and "manhã" is no
exception even though it is unambiguous on its own.

English, French and Italian resolve the bare morning word, and Portuguese
could look like a candidate for the same treatment: its word for tomorrow is
"amanhã", a different word, so "manhã" carries only the day-part sense.  The
obstacle is not "manhã" but the slot.  A grammar order binds the DAYPART slot,
and that slot holds every day-part surface the locale ships; there is no order
that admits "manhã" and refuses its siblings.  Admitting the bare form would
therefore also admit bare "tarde", which is equally the adverb *late* -- "mais
tarde", "cheguei tarde", "é tarde demais" would all answer a confident
afternoon band for sentences that name no time.  A wrong span is worse than no
span, so the bare order stays off for the whole locale.

What Portuguese actually says instead is framed, and every frame resolves:
"de manhã", "pela manhã", "a manhã", "esta manhã".  Nothing is unreachable;
only the bare noun is.

Gold bands are the pt row of the CLDR table transcribed in
:mod:`chronologia.dayparts` -- madrugada ``[00:00, 06:00)``, manhã
``[06:00, 12:00)``, tarde ``[12:00, 19:00)``, noite ``[19:00, 24:00)`` -- on
the anchor's own day, 2017-06-27.
"""
import pytest

from ._corpus import AstroDate, nomatch, parse


@pytest.mark.parametrize("text", [
    "manhã", "tarde", "noite", "madrugada",
    "mais tarde", "cheguei tarde", "é tarde demais",
])
def test_bare_daypart_word_is_not_a_span(text):
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
