"""Deliberate v1 omissions, pinned as refusals rather than left undocumented,
and the "nedelja"/"sedmica" week-vs-Sunday disambiguation.

"nedelja" names BOTH the weekday Sunday and, in some sources, the week --
Wiktionary marks the week sense secondary/regional and sr.wikipedia treats
"sedmica" as the unmarked week word, with the two conflicting on which is
primary.  This locale resolves the ambiguity by CONSTRUCTION: "nedelja"
binds only the WEEKDAY slot (weekday_6.voc), and the duration unit is
"sedmica" alone (unit_week.voc) -- "nedelja" never enters a duration
reading.

Two shapes of that ambiguity are refused outright rather than guessed:

* "nedelju dana" ("a week [of days]") -- the trailing "dana" is the exact
  cue that means WEEK in real speech, but expressing that reading needs
  grammar machinery this family does not have (no construction lets a
  bare weekday match widen into a week offset the way a genitive
  reinforcement noun does elsewhere).  Silently answering the lone-Sunday
  sub-reading and stranding "dana" would be a worse wrong answer than
  none, so the weekday match is vetoed whenever a bare day-unit word
  trails it and the whole phrase refuses.
* "prošle/sledeće nedelje" (the genitive case) -- dictionaries give "last
  WEEK" as the default gloss of this exact genitive, conflicting with the
  weekday reading the bare nominative gets; no source establishes one
  reading as dominant, so it refuses rather than silently picking one.

"milenijum" (millennium) ships no declension table in the sources consulted
and is excluded from every unit file -- a bare or "pre X" millennium phrase
must refuse rather than guess a duration.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, parse, span, start


# -- nedelja: weekday reading works, preposition consumed --------------------

@pytest.mark.parametrize("phrase", ["nedelju", "недељу"])
def test_bare_nedelju_is_sunday(phrase):
    """"nedelju" alone (the accusative weekday form) resolves to the next
    Sunday -- the WEEKDAY sense, never a week-long span."""
    s = span(phrase)
    assert (s.end - s.start) == timedelta(days=1)
    assert s.start.date().weekday() == 6  # Sunday


@pytest.mark.parametrize("phrase", ["u nedelju", "у недељу"])
def test_u_nedelju_consumes_the_preposition(phrase):
    """The day preposition "u"/"у" is consumed by the weekday_ref match, not
    left stranded in the remainder."""
    r = parse(phrase)
    assert r is not None
    assert r[0].start.date().weekday() == 6
    assert r[1] == ""


@pytest.mark.parametrize("phrase", ["sledeća nedelja", "prošla nedelja",
                                    "следећа недеља", "прошла недеља"])
def test_nedelja_nominative_as_weekday_determiner(phrase):
    """The NOMINATIVE "prošla/sledeća nedelja" is unambiguously the weekday
    determiner shape ("next/last Sunday") -- only the GENITIVE case
    ("nedelje", below) collides with the week sense."""
    r = parse(phrase)
    assert r is not None
    assert r[0].start.date().weekday() == 6


# -- nedelja: duration/genitive readings REFUSED -----------------------------

@pytest.mark.parametrize("phrase", [
    "nedelju dana", "za nedelju dana", "pre nedelju dana",
    "недељу дана", "за недељу дана", "пре недељу дана",
])
def test_nedelja_dana_refuses_rather_than_stranding_dana(phrase):
    """"nedelju dana" ("a week [of days]") is a real colloquial phrase, but
    with no grammar to express the disambiguated WEEK reading, answering
    the lone-Sunday sub-reading and stranding "dana" would be a worse wrong
    answer than none -- so the whole phrase refuses."""
    nomatch(phrase)


@pytest.mark.parametrize("phrase", [
    "prošle nedelje", "sledeće nedelje", "прошле недеље", "следеће недеље",
])
def test_genitive_nedelje_refuses_last_next(phrase):
    """"prošle/sledeće nedelje" (genitive) is genuinely ambiguous: no cited
    source establishes whether "last week" or "last Sunday" dominates, so
    the phrase refuses rather than silently picking a sense."""
    nomatch(phrase)


def test_sedmica_is_the_unambiguous_week_word():
    """"sedmica" (never "nedelja") is the duration-unit surface for a
    week -- confirms the disambiguation actually lands on the unambiguous
    word."""
    assert start("pre jedna sedmica") == ad(ANCHOR - timedelta(weeks=1))
    assert start("pre pet sedmica") == ad(ANCHOR - timedelta(weeks=5))


@pytest.mark.parametrize("phrase", ["za sedmicu", "за седмицу"])
def test_za_sedmicu_bare_unit_offset(phrase):
    """The bare-unit MARKER USG offset ("za sedmicu" = "in a week") --
    accusative "sedmicu" after "za", the same mechanism pl/uk/sk/bg/hr/cs
    use for their own bare-unit offsets."""
    r = span(phrase)
    assert r.start == ad(ANCHOR + timedelta(weeks=1))


@pytest.mark.parametrize("phrase", ["pre sedmice", "пре седмице"])
def test_pre_sedmice_bare_unit_offset(phrase):
    """"pre sedmice" ("a week ago") -- genitive singular "sedmice" after
    "pre", the ago-direction mirror of "za sedmicu"."""
    r = span(phrase)
    assert r.start == ad(ANCHOR - timedelta(weeks=1))


# -- milenijum: excluded, no declension table found --------------------------

@pytest.mark.parametrize("phrase", [
    "milenijum", "pre milenijum", "za jedan milenijum", "pre dva milenijuma",
    "миленијум", "пре миленијум",
])
def test_milenijum_refuses(phrase):
    """No Wiktionary declension table was found for "milenijum" -- it ships
    no unit file in any script, so every phrasing refuses rather than
    guessing an undocumented paradigm."""
    nomatch(phrase)
