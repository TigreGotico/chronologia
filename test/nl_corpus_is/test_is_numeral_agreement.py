"""Numeral agreement: one to four inflect, five and up never do.

Icelandic numerals are not governed by a counting rule -- 1..4 are strong
adjectives agreeing in case, gender and number with the noun they count, and
everything from five up is an invariant token.  A compound inflects its last
element only, so 21 agrees on its one and a teen (a single invariant word)
agrees not at all.

The gold here is the rule itself, stated independently of the parser: which
numbers inflect is written out in :data:`INFLECTING` by hand, the expected
surfaces are written out by hand from the declension tables, the phrase is
assembled from :func:`counted_phrase`, and only then is the assembled phrase
handed to the extractor.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.extract.numfold_icelandic import (ACCUSATIVE, DATIVE,
                                                   FEMININE, GENITIVE,
                                                   MASCULINE, NEUTER,
                                                   NOMINATIVE, UNIT_FORMS,
                                                   counted_phrase,
                                                   inflecting_element,
                                                   numeral_surface, read_run,
                                                   unit_surface)

from ._corpus import ANCHOR, ad, start

#: the numbers whose final element inflects, written out independently of the
#: implementation: a last digit of 1..4, except inside a teen.
INFLECTING = {
    1: 1, 2: 2, 3: 3, 4: 4, 5: None, 9: None, 10: None,
    11: None, 12: None, 13: None, 14: None, 19: None, 20: None,
    21: 1, 22: 2, 23: 3, 24: 4, 25: None, 30: None, 31: 1,
    100: None, 101: 1, 102: 2, 110: None, 111: None, 114: None, 121: 1,
}


@pytest.mark.parametrize("n,expected", sorted(INFLECTING.items()))
def test_inflecting_element(n, expected):
    assert inflecting_element(n) == expected


@pytest.mark.parametrize("n", [11, 12, 13, 14, 15, 16, 17, 18, 19,
                               111, 112, 113, 114])
def test_teens_never_inflect(n):
    """A teen ends in a 1..4 digit but is one invariant word, so the last-digit
    reading a Baltic-style fold would apply is wrong here."""
    assert inflecting_element(n) is None


@pytest.mark.parametrize("n", [5, 6, 7, 8, 9, 10, 20, 25, 30, 40, 99, 100])
def test_five_and_up_are_invariant(n):
    """The surface is the same in every case and gender."""
    forms = {numeral_surface(n, g, c)
             for g in (MASCULINE, FEMININE, NEUTER)
             for c in (NOMINATIVE, ACCUSATIVE, DATIVE, GENITIVE)}
    assert len(forms) == 1


# -- the four paradigms, written out from the declension tables -------------

@pytest.mark.parametrize("n,case,gender,expected", [
    (1, NOMINATIVE, MASCULINE, "einn"),
    (1, NOMINATIVE, FEMININE, "ein"),
    (1, NOMINATIVE, NEUTER, "eitt"),
    (1, ACCUSATIVE, MASCULINE, "einn"),
    (1, ACCUSATIVE, FEMININE, "eina"),
    (1, ACCUSATIVE, NEUTER, "eitt"),
    (1, DATIVE, MASCULINE, "einum"),
    (1, DATIVE, FEMININE, "einni"),
    (1, DATIVE, NEUTER, "einu"),
    (1, GENITIVE, MASCULINE, "eins"),
    (1, GENITIVE, FEMININE, "einnar"),
    (1, GENITIVE, NEUTER, "eins"),
    (2, NOMINATIVE, MASCULINE, "tveir"),
    (2, NOMINATIVE, FEMININE, "tvær"),
    (2, NOMINATIVE, NEUTER, "tvö"),
    (2, ACCUSATIVE, MASCULINE, "tvo"),
    (2, ACCUSATIVE, FEMININE, "tvær"),
    (2, ACCUSATIVE, NEUTER, "tvö"),
    (2, DATIVE, NEUTER, "tveimur"),
    (2, GENITIVE, FEMININE, "tveggja"),
    (3, NOMINATIVE, MASCULINE, "þrír"),
    (3, NOMINATIVE, FEMININE, "þrjár"),
    (3, NOMINATIVE, NEUTER, "þrjú"),
    (3, ACCUSATIVE, MASCULINE, "þrjá"),
    (3, ACCUSATIVE, FEMININE, "þrjár"),
    (3, DATIVE, MASCULINE, "þremur"),
    (3, GENITIVE, NEUTER, "þriggja"),
    (4, NOMINATIVE, MASCULINE, "fjórir"),
    (4, NOMINATIVE, FEMININE, "fjórar"),
    (4, NOMINATIVE, NEUTER, "fjögur"),
    (4, ACCUSATIVE, MASCULINE, "fjóra"),
    (4, ACCUSATIVE, NEUTER, "fjögur"),
    (4, DATIVE, FEMININE, "fjórum"),
    (4, GENITIVE, MASCULINE, "fjögurra"),
])
def test_numeral_paradigm(n, case, gender, expected):
    assert numeral_surface(n, gender, case) == expected


@pytest.mark.parametrize("n,gender,case,expected", [
    (21, MASCULINE, NOMINATIVE, "tuttugu og einn"),
    (21, NEUTER, NOMINATIVE, "tuttugu og eitt"),
    (22, FEMININE, ACCUSATIVE, "tuttugu og tvær"),
    (23, MASCULINE, DATIVE, "tuttugu og þremur"),
    (24, NEUTER, ACCUSATIVE, "tuttugu og fjögur"),
    (31, MASCULINE, NOMINATIVE, "þrjátíu og einn"),
    (25, MASCULINE, DATIVE, "tuttugu og fimm"),
    (101, MASCULINE, NOMINATIVE, "hundrað og einn"),
    (100, NEUTER, NOMINATIVE, "hundrað"),
    (200, NEUTER, NOMINATIVE, "tvö hundruð"),
])
def test_compound_inflects_its_last_element(n, gender, case, expected):
    assert numeral_surface(n, gender, case) == expected


def test_only_the_last_element_moves():
    """The tens word is the same in every case; only the one after it moves."""
    assert numeral_surface(21, MASCULINE, NOMINATIVE) == "tuttugu og einn"
    assert numeral_surface(21, MASCULINE, DATIVE) == "tuttugu og einum"


@pytest.mark.parametrize("n", [-1, 1000, 247, 2020])
def test_unattested_magnitudes_are_refused(n):
    """A numeral shape no source shows is refused rather than composed."""
    with pytest.raises(ValueError):
        numeral_surface(n)


# -- the counted noun -------------------------------------------------------

@pytest.mark.parametrize("kind", sorted(UNIT_FORMS))
def test_every_unit_has_all_eight_forms(kind):
    forms = UNIT_FORMS[kind]
    wanted = {c + s for c in ("nom", "acc", "dat", "gen") for s in ("", "_pl")}
    assert wanted <= set(forms)
    assert all(forms[k] for k in wanted)
    assert forms["gender"] in (MASCULINE, FEMININE, NEUTER)


@pytest.mark.parametrize("kind,case,expected", [
    ("day", NOMINATIVE, "dagur"), ("day", ACCUSATIVE, "dag"),
    ("day", DATIVE, "degi"), ("day", GENITIVE, "dags"),
    ("week", DATIVE, "viku"), ("year", DATIVE, "ári"),
    ("month", GENITIVE, "mánaðar"), ("century", GENITIVE, "aldar"),
])
def test_singular_unit_surface(kind, case, expected):
    assert unit_surface(1, kind, case) == expected


@pytest.mark.parametrize("kind,case,expected", [
    ("day", NOMINATIVE, "dagar"), ("day", ACCUSATIVE, "daga"),
    ("day", DATIVE, "dögum"),
    ("week", ACCUSATIVE, "vikur"), ("week", DATIVE, "vikum"),
    ("month", ACCUSATIVE, "mánuði"), ("month", DATIVE, "mánuðum"),
    ("year", ACCUSATIVE, "ár"), ("year", DATIVE, "árum"),
    ("century", NOMINATIVE, "aldir"), ("century", DATIVE, "öldum"),
    ("minute", ACCUSATIVE, "mínútur"), ("minute", DATIVE, "mínútum"),
])
def test_plural_unit_surface(kind, case, expected):
    assert unit_surface(5, kind, case) == expected


def test_compound_ending_in_one_refuses_a_noun_number():
    """Whether "tuttugu og einn dagur" keeps the singular is not attested, so
    the helper refuses rather than putting a guess into a test's gold."""
    with pytest.raises(ValueError):
        unit_surface(21, "day")


# -- the rule, end to end ---------------------------------------------------
# The phrase is built from the rule's own output, so a wrong surface would be
# a wrong phrase and the extractor would refuse it rather than quietly agree.

@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 10, 11, 12, 20, 30, 100])
def test_days_ago_across_the_agreement_classes(n):
    phrase = f"fyrir {counted_phrase(n, 'day', DATIVE)}"
    assert start(phrase) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 12, 20])
def test_days_ahead_across_the_agreement_classes(n):
    phrase = f"eftir {counted_phrase(n, 'day', ACCUSATIVE)}"
    assert start(phrase) == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 11, 20])
def test_weeks_across_the_genders(n):
    """Weeks are feminine, days masculine, years neuter -- the same count
    spells its numeral differently in each."""
    assert start(f"fyrir {counted_phrase(n, 'week', DATIVE)}") == ad(
        ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 10, 100])
def test_years_across_the_genders(n):
    assert start(f"fyrir {counted_phrase(n, 'year', DATIVE)}") == ad(
        ANCHOR - relativedelta(years=n))


@pytest.mark.parametrize("n", [2, 3, 4, 5, 15, 30, 45])
def test_minutes_across_the_agreement_classes(n):
    assert start(f"eftir {counted_phrase(n, 'minute', ACCUSATIVE)}") == ad(
        ANCHOR + timedelta(minutes=n))


@pytest.mark.parametrize("phrase,n,gender_note", [
    ("fyrir einum degi", 1, "masculine"),
    ("fyrir tveimur dögum", 2, "masculine"),
    ("fyrir þremur dögum", 3, "masculine"),
    ("fyrir fjórum dögum", 4, "masculine"),
    ("fyrir fimm dögum", 5, "invariant"),
    ("fyrir ellefu dögum", 11, "invariant"),
])
def test_hand_written_offsets(phrase, n, gender_note):
    assert start(phrase) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("phrase,delta", [
    ("eftir eina viku", timedelta(weeks=1)),
    ("eftir tvær vikur", timedelta(weeks=2)),
    ("eftir þrjár vikur", timedelta(weeks=3)),
    ("eftir fjórar vikur", timedelta(weeks=4)),
    ("eftir fimm vikur", timedelta(weeks=5)),
])
def test_feminine_week_agreement(phrase, delta):
    """The feminine accusative of two is "tvær", not the masculine "tvo": a
    fold that ignored gender would spell -- and read -- the wrong word."""
    assert start(phrase) == ad(ANCHOR + delta)


@pytest.mark.parametrize("phrase,n", [
    ("eftir eitt ár", 1), ("eftir tvö ár", 2), ("eftir þrjú ár", 3),
    ("eftir fjögur ár", 4), ("eftir fimm ár", 5),
])
def test_neuter_year_agreement(phrase, n):
    assert start(phrase) == ad(ANCHOR + relativedelta(years=n))


@pytest.mark.parametrize("phrase,value", [
    ("tuttugu og einn", 21), ("þrjátíu og tveir", 32),
    ("hundrað og fimm", 105), ("fimm hundruð", 500), ("eitt þúsund", 1000),
    ("níutíu og níu", 99), ("ellefu", 11), ("núll", 0),
])
def test_run_reader(phrase, value):
    assert read_run(phrase) == value


@pytest.mark.parametrize("phrase", ["og", "júní", "dagur", "hálf"])
def test_run_reader_refuses_a_non_number(phrase):
    assert read_run(phrase) is None
