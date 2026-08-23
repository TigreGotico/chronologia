"""Esperanto UNIT recurrence: "ĉiu(n)" (every/each) + a unit noun.

Three attested shapes are wired:

* the univerbated adverb "ĉiutage"/"ĉiusemajne"/"ĉiumonate"/"ĉiujare" --
  "ĉiu-" (every) + the unit stem + the adverbial "-e", a single fixed
  token (en.wiktionary.org "ĉiu", sense list);
* the periphrastic determiner+noun "ĉiu UNIT" -- nominative, "Ĉiu tago
  daŭras dudek kvar horojn" (Each day lasts 24 hours), same source;
* the periphrastic ACCUSATIVE "ĉiun UNITn" -- "ĉiun" is the regular
  accusative of "ĉiu", governing the accusative on the noun it
  distributes over exactly as any Esperanto adjective/determiner agrees
  with its noun's case (en.wikipedia.org "Esperanto grammar").

day/week/month/year are the only units RFC-5545-mapped by chronologia's
shared recurrence engine (``chronologia.extract.nseries._UNIT_FREQ``) --
an engine-wide constraint, not an Esperanto-specific gap, so second,
hour, decade, century and millennium recurrence are refused across every
locale and pinned as refusals here too.
"""
import pytest

from chronologia import extract_recurrence

from ._corpus import ANCHOR


def _recur(text):
    return extract_recurrence(text, "eo", ANCHOR)


@pytest.mark.parametrize("text,freq", [
    ("ĉiutage", "DAILY"), ("ĉiusemajne", "WEEKLY"),
    ("ĉiumonate", "MONTHLY"), ("ĉiujare", "YEARLY"),
])
def test_fused_adverb_names_the_frequency(text, freq):
    got = _recur(text)
    assert got is not None
    assert got.recurrence.freq == freq
    assert got.recurrence.interval == 1


@pytest.mark.parametrize("text,freq", [
    ("ĉiu tago", "DAILY"), ("ĉiu semajno", "WEEKLY"),
    ("ĉiu monato", "MONTHLY"), ("ĉiu jaro", "YEARLY"),
])
def test_nominative_periphrasis_names_the_frequency(text, freq):
    got = _recur(text)
    assert got is not None
    assert got.recurrence.freq == freq


@pytest.mark.parametrize("text,freq", [
    ("ĉiun tagon", "DAILY"), ("ĉiun semajnon", "WEEKLY"),
    ("ĉiun monaton", "MONTHLY"), ("ĉiun jaron", "YEARLY"),
])
def test_accusative_periphrasis_names_the_frequency(text, freq):
    """"ĉiun UNITn" -- the accusative periphrasis: "ĉiun" governs the
    accusative on the unit noun it distributes over."""
    got = _recur(text)
    assert got is not None
    assert got.recurrence.freq == freq


def test_fused_and_periphrastic_forms_agree():
    assert _recur("ĉiutage").recurrence == _recur("ĉiu tago").recurrence
    assert _recur("ĉiutage").recurrence == _recur("ĉiun tagon").recurrence


@pytest.mark.parametrize("text", [
    "ĉiu sekundo", "ĉiun sekundon", "ĉiu horo", "ĉiun horon",
    "ĉiu jardeko", "ĉiun jardekon", "ĉiu jarcento", "ĉiu jarmilo",
])
def test_units_outside_the_shared_engine_s_freq_map_are_refused(text):
    """second/hour/decade/century/millennium have no RFC-5545 FREQ mapping
    anywhere in chronologia (``_UNIT_FREQ``) -- an engine-wide limit this
    locale inherits, not a gap of its own, so no locale can attest these."""
    assert _recur(text) is None


@pytest.mark.parametrize("text", ["ĉiu", "ĉiun", "tage", "semajne"])
def test_incomplete_or_unwired_forms_refuse(text):
    """A bare "ĉiu"/"ĉiun" with nothing to distribute over, and a bare
    adverbial UNIT stem with no leading "ĉiu-" (chronologia's fused-adverb
    slot only reads the whole univerbated word, not its parts), refuse."""
    assert _recur(text) is None
