"""Definiteness and case on the counted noun, construction by construction.

Albanian does not have one word for "day" that fits everywhere.  ``pas``
governs the ablative, ``më parë``/``para`` leave the noun indefinite,
``këtë``/``çdo`` take it bare, and only the fused ``e kaluar`` /
``e ardhshëm`` frame puts it in the definite accusative.  The gold below is
CLDR 47's ``dateFields.json`` for ``sq`` (which spells one pattern per
construction) cross-checked against en.wiktionary.org's declension tables --
not read back off the fold's own tables, which is why the surfaces are
written out here rather than generated from ``UNIT_FORMS``.
"""
import pytest

from chronologia.extract.numfold_albanian import (ABLATIVE_PLURAL,
                                                  ABLATIVE_SINGULAR,
                                                  DEFINITE_ACCUSATIVE,
                                                  INDEFINITE,
                                                  INDEFINITE_PLURAL,
                                                  governed_form, three,
                                                  unit_surface)

from ._corpus import start, start_end


# -- the rule, stated as a table --------------------------------------------

@pytest.mark.parametrize("marker,count,form", [
    ("pas", 1, ABLATIVE_SINGULAR),
    ("pas", 2, ABLATIVE_PLURAL),
    ("pas", 11, ABLATIVE_PLURAL),
    ("më parë", 1, INDEFINITE),
    ("më parë", 2, INDEFINITE_PLURAL),
    ("para", 1, INDEFINITE),
    ("para", 7, INDEFINITE_PLURAL),
    ("këtë", 1, INDEFINITE),
    ("çdo", 1, INDEFINITE),
    ("e kaluar", 1, DEFINITE_ACCUSATIVE),
    ("e ardhshëm", 1, DEFINITE_ACCUSATIVE),
    ("e ardhshme", 1, DEFINITE_ACCUSATIVE),
])
def test_the_governing_word_picks_the_form(marker, count, form):
    assert governed_form(marker, count) == form


def test_an_unknown_governor_is_refused():
    with pytest.raises(KeyError):
        governed_form("midis")


@pytest.mark.parametrize("kind,marker,count,surface", [
    ("day", "pas", 1, "dite"),
    ("day", "pas", 3, "ditësh"),
    ("day", "më parë", 1, "ditë"),
    ("day", "më parë", 3, "ditë"),
    ("day", "këtë", 1, "ditë"),
    ("day", "e kaluar", 1, "ditën"),
    ("week", "pas", 1, "jave"),
    ("week", "pas", 2, "javësh"),
    ("week", "më parë", 1, "javë"),
    ("week", "e kaluar", 1, "javën"),
    ("month", "pas", 1, "muaji"),
    ("month", "pas", 2, "muajsh"),
    ("month", "më parë", 2, "muaj"),
    ("month", "e ardhshëm", 1, "muajin"),
    ("year", "pas", 1, "viti"),
    ("year", "pas", 2, "vjetësh"),
    ("year", "më parë", 1, "vit"),
    ("year", "më parë", 2, "vjet"),
    ("year", "e kaluar", 1, "vitin"),
    ("hour", "pas", 1, "ore"),
    ("hour", "pas", 6, "orësh"),
    ("hour", "më parë", 2, "orë"),
    ("minute", "pas", 1, "minute"),
    ("minute", "pas", 10, "minutash"),
    ("minute", "më parë", 1, "minutë"),
    ("minute", "më parë", 10, "minuta"),
    ("second", "pas", 1, "sekonde"),
    ("second", "pas", 30, "sekondash"),
    ("second", "më parë", 30, "sekonda"),
    ("century", "para", 3, "shekuj"),
    ("century", "pas", 3, "shekujsh"),
])
def test_the_surface_each_construction_takes(kind, marker, count, surface):
    assert unit_surface(kind, marker, count) == surface


def test_the_year_stem_is_suppletive():
    """Only the year changes stem between its singular and its plural, which
    is why a rule generated from the singular would produce "vitësh"."""
    assert unit_surface("year", "më parë", 1) == "vit"
    assert unit_surface("year", "më parë", 4) == "vjet"
    assert unit_surface("year", "pas", 4) == "vjetësh"


@pytest.mark.parametrize("kind,word", [
    ("day", "tri"), ("week", "tri"), ("hour", "tri"), ("minute", "tri"),
    ("second", "tri"), ("month", "tre"), ("year", "tre"), ("century", "tre"),
])
def test_three_agrees_with_the_units_gender(kind, word):
    assert three(kind) == word


def test_an_unknown_unit_has_no_three():
    with pytest.raises(KeyError):
        three("fortnight")


# -- and the same rule, read end to end through the parser ------------------

@pytest.mark.parametrize("text,days", [
    ("pas një dite", 1), ("pas tri ditësh", 3), ("pas shtatë ditësh", 7),
])
def test_the_ablative_after_pas_parses(text, days):
    from datetime import timedelta

    from ._corpus import ANCHOR
    assert start(text).day == (ANCHOR + timedelta(days=days)).day


@pytest.mark.parametrize("text,days", [
    ("një ditë më parë", 1), ("tri ditë më parë", 3),
    ("shtatë ditë më parë", 7),
])
def test_the_indefinite_before_more_pare_parses(text, days):
    from datetime import timedelta

    from ._corpus import ANCHOR
    assert start(text).day == (ANCHOR - timedelta(days=days)).day


@pytest.mark.parametrize("text,first_of_month", [
    ("këtë muaj", 6), ("muajin e kaluar", 5), ("muajin e ardhshëm", 7),
])
def test_the_bare_and_definite_month_frames_parse(text, first_of_month):
    s, _ = start_end(text)
    assert (s.month, s.day) == (first_of_month, 1)


def test_the_bare_noun_and_the_definite_noun_are_different_words():
    """"këtë javë" and "javën e ardhshme" name adjacent weeks with DIFFERENT
    forms of the same noun; a locale shipping one form everywhere would parse
    only one of the two."""
    this_week, _ = start_end("këtë javë")
    next_week, _ = start_end("javën e ardhshme")
    assert (this_week.year, this_week.month, this_week.day) == (2017, 6, 26)
    assert (next_week.year, next_week.month, next_week.day) == (2017, 7, 3)
