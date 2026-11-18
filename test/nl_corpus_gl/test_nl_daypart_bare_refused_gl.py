# -*- coding: utf-8 -*-
"""Galician keeps both readings of "mañá" apart by requiring a frame.

The Dicionario da Real Academia Galega gives "mañá" two senses in one word:
the stretch of day between sunrise and midday, and the day after today.  Only
the second is available bare, because that is the reading a lone "mañá"
carries in speech; the day-part sense needs an article, a contraction with
"por", or a preposition in front of it -- "pola mañá", "a mañá", "esta mañá".
"en mañá" keeps the tomorrow reading and leaves its preposition alone.

The other three words are refused bare for the reason Portuguese and Spanish
refuse theirs: "tarde" is also the adverb *late*, and one grammar order binds
every day-part surface the locale ships, so admitting a bare "mañá" would
admit a bare "tarde" with it.

Gold bands are the gl row of the CLDR table transcribed in
:mod:`chronologia.dayparts` -- madrugada ``[00:00, 06:00)``, mañá
``[06:00, 12:00)``, tarde ``[13:00, 21:00)``, noite ``[21:00, 24:00)`` -- on
the anchor's own day, 2017-06-27.
"""
import pytest

from ._corpus import AstroDate, nomatch, parse


@pytest.mark.parametrize("text", ["tarde", "noite", "madrugada", "máis tarde"])
def test_bare_daypart_word_is_not_a_span(text):
    nomatch(text)


def test_bare_mana_is_tomorrow():
    r = parse("mañá")
    assert (r.span.start, r.span.end) == (AstroDate(2017, 6, 28),
                                          AstroDate(2017, 6, 29))
    assert r.remainder == ""


def test_en_mana_stays_tomorrow():
    r = parse("en mañá")
    assert (r.span.start, r.span.end) == (AstroDate(2017, 6, 28),
                                          AstroDate(2017, 6, 29))


# a band that has ended at the 13:04 anchor is tomorrow's, unless "esta"
# names today (ruling 28)
@pytest.mark.parametrize("text,lo,hi,day", [
    ("pola mañá", 6, 12, 28),
    ("a mañá", 6, 12, 28),
    ("esta mañá", 6, 12, 27),
    ("á tarde", 13, 21, 27),
    ("pola tarde", 13, 21, 27),
    ("pola noite", 21, 24, 27),
    ("esta noite", 21, 24, 27),
    ("de madrugada", 0, 6, 28),
    ("pola madrugada", 0, 6, 28),
])
def test_the_framed_form_resolves(text, lo, hi, day):
    r = parse(text)
    assert r is not None, text
    end = (AstroDate(2017, 6, day + 1, 0, 0, 0) if hi == 24
           else AstroDate(2017, 6, day, hi, 0, 0))
    assert (r.span.start, r.span.end) == (AstroDate(2017, 6, day, lo, 0, 0), end)
    assert r.remainder == "", f"{text!r} stranded {r.remainder!r}"
