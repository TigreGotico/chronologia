"""Two independent systems decide the form of a counted Latvian noun.

The first is government by a duration marker: "pirms" and "pēc" put their
phrase in the dative, and the unit noun is the genitive SINGULAR when the
numeral ends in 1 and is not 11, the DATIVE PLURAL otherwise -- "pirms gada",
"pirms 21 gada", "pirms 11 gadiem", "pirms 20 gadiem".  Note the plural is
the dative (gadiem, dienām), not the genitive plural (gadu, dienu); the two
are distinct in every Latvian declension.

The second is the register split of a bare count: after 11-19 and the round
tens a formal text puts the noun in the genitive plural ("vienpadsmit gadu")
where a colloquial one leaves it in the nominative ("vienpadsmit gadi").  No
source gives a mechanical trigger for which register a text is written in, so
both surfaces are accepted and neither is ever inferred from the input.  The
tests below assert exactly that: both readings resolve, and to the same span.

The gold is the rule itself, written out here by hand before any phrase is
assembled, so a wrong surface in the implementation makes a wrong phrase that
the extractor refuses rather than quietly agrees with.
"""
from datetime import timedelta

import pytest

from chronologia.extract.numfold_latvian import (DATIVE_PLURAL,
                                                 GENITIVE_PLURAL,
                                                 GENITIVE_SINGULAR, NOMINATIVE,
                                                 UNIT_FORMS, counting_registers,
                                                 governed_form, read_run,
                                                 unit_surface)

from ._corpus import ANCHOR, ad, nomatch, start

#: the form a duration marker imposes, per numeral, written out independently
#: of the implementation.
GOVERNED = {
    1: GENITIVE_SINGULAR, 2: DATIVE_PLURAL, 3: DATIVE_PLURAL,
    9: DATIVE_PLURAL, 10: DATIVE_PLURAL, 11: DATIVE_PLURAL,
    12: DATIVE_PLURAL, 19: DATIVE_PLURAL, 20: DATIVE_PLURAL,
    21: GENITIVE_SINGULAR, 22: DATIVE_PLURAL, 30: DATIVE_PLURAL,
    31: GENITIVE_SINGULAR, 100: DATIVE_PLURAL, 101: GENITIVE_SINGULAR,
    111: DATIVE_PLURAL, 121: GENITIVE_SINGULAR,
}


@pytest.mark.parametrize("n,expected", sorted(GOVERNED.items()))
def test_governed_form(n, expected):
    assert governed_form(n) == expected


@pytest.mark.parametrize("n", [11, 111, 211])
def test_eleven_is_the_exception_to_the_final_one_rule(n):
    assert governed_form(n) == DATIVE_PLURAL


@pytest.mark.parametrize("n", [1, 21, 31, 41, 101, 121, 1001])
def test_final_one_takes_the_genitive_singular(n):
    assert governed_form(n) == GENITIVE_SINGULAR


@pytest.mark.parametrize("kind", sorted(UNIT_FORMS))
def test_every_unit_carries_every_form(kind):
    forms = UNIT_FORMS[kind]
    assert {"nom", "nom_sg", "gen_sg", "gen_pl", "dat_pl", "acc_sg",
            "loc_sg"} <= set(forms)
    assert all(forms[k] for k in forms)


@pytest.mark.parametrize("kind", sorted(UNIT_FORMS))
def test_dative_plural_differs_from_genitive_plural(kind):
    """The distinction the CLDR patterns turn on: "pirms 11 gadiem" is the
    dative, and "gadu" -- the genitive plural -- is a different word."""
    forms = UNIT_FORMS[kind]
    assert forms["dat_pl"] != forms["gen_pl"]


# -- government, end to end -------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3, 9, 10, 11, 12, 19, 20, 21, 22, 30, 31])
def test_days_ago_across_the_government(n):
    phrase = f"pirms {n} {unit_surface(n, 'day', governed_form(n))}"
    assert start(phrase) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n", [1, 2, 5, 11, 20, 21])
def test_weeks_ago_across_the_government(n):
    phrase = f"pirms {n} {unit_surface(n, 'week', governed_form(n))}"
    assert start(phrase) == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n", [2, 3, 11, 20, 25, 45])
def test_minutes_ago_across_the_government(n):
    phrase = f"pirms {n} {unit_surface(n, 'minute', governed_form(n))}"
    assert start(phrase) == ad(ANCHOR - timedelta(minutes=n))


@pytest.mark.parametrize("n", [1, 2, 3, 11, 20, 21])
def test_days_ahead_across_the_government(n):
    phrase = f"pēc {n} {unit_surface(n, 'day', governed_form(n))}"
    assert start(phrase) == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n", [2, 3, 12, 30])
def test_hours_ahead_across_the_government(n):
    phrase = f"pēc {n} {unit_surface(n, 'hour', governed_form(n))}"
    assert start(phrase) == ad(ANCHOR + timedelta(hours=n))


@pytest.mark.parametrize("n,form", [
    (1, "dienas"), (2, "dienām"), (11, "dienām"), (21, "dienas"),
    (30, "dienām"),
])
def test_governed_surface_matches_the_rule(n, form):
    assert unit_surface(n, "day", governed_form(n)) == form


# -- the register split -----------------------------------------------------

@pytest.mark.parametrize("n", [11, 12, 19, 10, 20, 30, 100, 111, 119])
def test_the_split_range_admits_both_registers(n):
    assert counting_registers(n) == (NOMINATIVE, GENITIVE_PLURAL)


@pytest.mark.parametrize("n", [1, 2, 3, 9, 21, 22, 25, 99, 101])
def test_outside_the_split_range_only_the_nominative(n):
    assert counting_registers(n) == (NOMINATIVE,)


@pytest.mark.parametrize("n", [11, 12, 19, 20, 30])
def test_both_registers_read_the_same_offset(n):
    """Formal "pirms vienpadsmit gadu" and the governed "pirms 11 gadiem"
    name the same moment; the parser accepts both and prefers neither."""
    formal = f"pirms {n} {UNIT_FORMS['year']['gen_pl']}"
    governed = f"pirms {n} {unit_surface(n, 'year', governed_form(n))}"
    assert start(formal) == start(governed)


@pytest.mark.parametrize("phrase,n", [
    ("pirms vienpadsmit gadiem", 11),
    ("pirms vienpadsmit gadu", 11),
    ("pirms divdesmit gadiem", 20),
    ("pirms divdesmit gadu", 20),
])
def test_spelled_numeral_in_both_registers(phrase, n):
    assert start(phrase).year == ANCHOR.year - n


@pytest.mark.parametrize("phrase,n", [
    ("pirms divām dienām", 2),
    ("pirms trim dienām", 3),
    ("pirms piecām dienām", 5),
    ("pirms desmit dienām", 10),
    ("pirms divdesmit piecām dienām", 25),
])
def test_spelled_dative_numeral_governs_its_noun(phrase, n):
    assert start(phrase) == ad(ANCHOR - timedelta(days=n))


# -- the run reader, on its own ---------------------------------------------

@pytest.mark.parametrize("text,value", [
    ("viens", 1), ("divi", 2), ("desmit", 10), ("vienpadsmit", 11),
    ("deviņpadsmit", 19), ("divdesmit", 20), ("divdesmit pieci", 25),
    ("deviņdesmit deviņi", 99), ("simts", 100), ("simts divdesmit pieci", 125),
    ("tūkstotis", 1000), ("divi tūkstoši", 2000),
    ("divi tūkstoši divdesmit pieci", 2025),
])
def test_read_run(text, value):
    assert read_run(text) == value


@pytest.mark.parametrize("text", ["divi simti", "trīs simti"])
def test_the_plural_of_the_hundred_is_not_read(text):
    """"simts" ships in the nominative and its attested synonym "simt" only:
    no dictionary consulted declines it, so a multiplied hundred is refused
    rather than spelled from a guessed paradigm."""
    assert read_run(text) is None


@pytest.mark.parametrize("text", ["gads", "maijs", "pirms", ""])
def test_read_run_refuses_a_non_numeral(text):
    assert read_run(text) is None


def test_a_teen_never_continues_a_run():
    """11-19 are whole numerals: "divdesmit vienpadsmit" is not 31, and not a
    number at all."""
    nomatch("pirms divdesmit vienpadsmit dienām")
