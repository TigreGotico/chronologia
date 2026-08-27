"""What this locale declines to answer, and why each refusal is the answer.

Every case here is an omission with a reason.  A locale that guessed at any of
them would return a confident wrong span for text a Swahili speaker writes,
which is worse than returning nothing, so each refusal is pinned as hard as the
readings that do ship.

The clock refusal is the largest of them and has a file of its own.
"""
import pytest

from chronologia.extract.loader import load_lang_spec

from ._corpus import day, nomatch, parse, start_end


# -- no century, no millennium, no decade -----------------------------------
# karne, milenia and muongo are real nouns and their classes are known -- karne
# and milenia are class 9/10, muongo is class 3/4 -- so their counted forms
# ("karne mbili", "miongo miwili") follow from the productive concord rule.
# But a rule is not an attestation: no source consulted this pass shows any of
# the three actually counted in running text, and chronologia's scope units are
# read from real usage rather than derived.  All three stay out.

@pytest.mark.parametrize("text", [
    "karne", "karne mbili", "karne mbili zilizopita", "karne hii",
    "karne iliyopita", "karne ijayo",
    "milenia", "milenia hii", "milenia iliyopita", "milenia mbili",
    "muongo", "muongo huu", "muongo uliopita", "muongo ujao",
    "miongo miwili", "miongo miwili iliyopita",
])
def test_the_larger_units_are_not_shipped(text):
    nomatch(text)


def test_the_units_that_do_ship_are_exactly_the_seven_cldr_counts():
    spec = load_lang_spec("sw")
    assert set(spec.units.values()) == {
        "second", "minute", "hour", "day", "week", "month", "year"}
    assert spec.scope_units == {}


# -- juma carries no agreement of its own -----------------------------------
# juma is class 5/6 and is the other word for a week -- it is the word inside
# every Juma- weekday name.  Its class has no entry in CLDR's relative-time
# data and no attested last/this/next form was found, so the mechanical
# ma-concord guess ("juma lililopita") is not shipped and juma is not a unit at
# all.  wiki already carries every week reading CLDR states, so nothing is lost.

@pytest.mark.parametrize("text", [
    "juma", "juma lililopita", "juma hili", "juma lijalo",
    "majuma", "majuma matatu", "majuma matatu yaliyopita",
])
def test_juma_is_not_a_week(text):
    nomatch(text)


def test_wiki_carries_the_week_instead():
    assert start_end("wiki hii") == (day(2027, 5, 8)[0], day(2027, 5, 15)[0])
    assert start_end("wiki ijayo") == (day(2027, 5, 15)[0], day(2027, 5, 22)[0])


def test_the_juma_weekday_names_are_unaffected():
    """Refusing the noun must not cost the seven names built on it."""
    assert start_end("Jumatatu") == day(2027, 5, 17)
    assert start_end("Jumamosi") == day(2027, 5, 15)


# -- no ordinal register -----------------------------------------------------
# Swahili has a second way of naming a month -- "mwezi wa kwanza" for January,
# the first month -- and a general ordinal built from a class-agreeing
# connective plus the cardinal stem.  CLDR does not carry the ordinal month
# register, the sources that do are tutorial-tier, and the connective's shape
# per class was not confirmed for the units this locale reads.  So no ordinal
# vocabulary ships and no ordinal reading is guessed.

@pytest.mark.parametrize("text", [
    "mwezi wa kwanza", "mwezi wa pili", "mwezi wa kumi na mbili",
    "siku ya kwanza", "mwaka wa kwanza", "Jumatatu ya kwanza ya Juni",
])
def test_the_ordinal_register_is_not_read(text):
    r = parse(text)
    assert r is None or r[1] != "", (
        f"{text!r} consumed an ordinal with no source for its form")


# -- no quarter --------------------------------------------------------------
# CLDR gives Swahili a quarter field, and it is the one unit whose relative
# forms use a different verb entirely ("robo ya mwaka inayofuata", the quarter
# that follows, not the ijayo/ujao the other units take).  chronologia's
# quarter constructions are built on a single quarter noun, and "robo ya mwaka"
# is three words with an internal genitive; the register is recorded in the
# research but not shipped.

@pytest.mark.parametrize("text", [
    "robo hii ya mwaka", "robo ya mwaka iliyopita",
    "robo ya mwaka inayofuata", "robo mbili zilizopita",
])
def test_the_quarter_is_not_shipped(text):
    r = parse(text)
    assert r is None or r[1] != ""


# -- no seasons --------------------------------------------------------------
# East Africa's year is divided by rains, not by the four temperate seasons,
# and no source consulted this pass gives boundaries for any of the Swahili
# season words.  Boundaries nobody stated are not invented.

@pytest.mark.parametrize("text", [
    "kiangazi", "masika", "vuli", "kipupwe",
])
def test_no_season_is_shipped(text):
    nomatch(text)


def test_the_locale_ships_no_season_vocabulary():
    assert load_lang_spec("sw").seasons == {}


# -- "since" is not read as past-anchoring its endpoint ----------------------
# English "since monday until friday" reaches BACK to the most recent Monday,
# because English keeps "since" and "from" apart and only "since" looks
# backwards.  Swahili's sources gloss kutoka and tangu together as "from/since"
# without separating the two senses, so the past-anchoring reading is not
# claimed: "tangu X hadi Y" reads forward like any other closed range, which is
# the library's own default for a language that does not distinguish them.

def test_a_closed_range_opened_by_tangu_reads_forward():
    assert start_end("tangu Jumatatu hadi Ijumaa") == (day(2027, 5, 17)[0],
                                                       day(2027, 5, 22)[0])


def test_the_open_since_range_still_reaches_back_to_the_anchor():
    s = start_end("tangu jana")
    assert s[0] == day(2027, 5, 11)[0]
    assert (s[1].hour, s[1].minute) == (13, 4)
