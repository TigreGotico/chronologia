"""Numeral government: the counted noun's form is chosen by the numeral.

Lithuanian keys the counted noun off the numeral's LAST digit rather than its
magnitude.  A numeral ending in 1 (but not 11) takes the singular, one ending
in 2-9 (but not 12-19) the plural, and one ending in 0 or falling in 11-19 the
genitive plural: 21 diena, 25 dienos, 20 dienų, 111 dienų.

The gold here is the rule itself, stated independently of the parser: the
expected class per number is written out in :data:`EXPECTED` by hand, the
phrase is assembled from :data:`UNIT_FORMS`, and only then is the assembled
phrase handed to the extractor.
"""
from datetime import timedelta

import pytest

from chronologia.extract.numfold_baltic import (GENITIVE_PLURAL, PLURAL,
                                                SINGULAR, UNIT_FORMS,
                                                governed_case, unit_surface)

from ._corpus import ANCHOR, ad, start

#: the governed class of a hand-picked spread of numerals, written out
#: independently of the implementation.
EXPECTED = {
    1: SINGULAR, 2: PLURAL, 3: PLURAL, 9: PLURAL,
    10: GENITIVE_PLURAL, 11: GENITIVE_PLURAL, 12: GENITIVE_PLURAL,
    19: GENITIVE_PLURAL, 20: GENITIVE_PLURAL,
    21: SINGULAR, 22: PLURAL, 29: PLURAL, 30: GENITIVE_PLURAL,
    31: SINGULAR, 100: GENITIVE_PLURAL, 101: SINGULAR, 102: PLURAL,
    110: GENITIVE_PLURAL, 111: GENITIVE_PLURAL, 121: SINGULAR,
}


@pytest.mark.parametrize("n,expected", sorted(EXPECTED.items()))
def test_governed_case(n, expected):
    assert governed_case(n) == expected


@pytest.mark.parametrize("n", [11, 12, 13, 14, 15, 16, 17, 18, 19])
def test_teens_take_the_genitive_plural(n):
    """The teens are the exception the last-digit rule turns on: 11 ends in a
    1 but does not take the singular."""
    assert governed_case(n) == GENITIVE_PLURAL


@pytest.mark.parametrize("n", [1, 21, 31, 41, 101, 121, 1001])
def test_final_one_takes_the_singular(n):
    assert governed_case(n) == SINGULAR


@pytest.mark.parametrize("kind", sorted(UNIT_FORMS))
def test_every_unit_has_all_three_forms(kind):
    forms = UNIT_FORMS[kind]
    assert {SINGULAR, PLURAL, GENITIVE_PLURAL, "acc_sg", "acc_pl"} <= set(forms)
    assert all(forms[k] for k in forms)


# -- the rule, end to end ---------------------------------------------------
# The phrase is built from the rule's own output, so a wrong surface would be
# a wrong phrase and the extractor would refuse it rather than quietly agree.

@pytest.mark.parametrize("n", [1, 2, 3, 9, 10, 11, 12, 19, 20, 21, 22, 30, 31])
def test_days_ago_across_the_government_classes(n):
    phrase = f"prieš {n} {unit_surface(n, 'day', accusative=True)}"
    assert start(phrase) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n", [1, 2, 5, 11, 20, 21])
def test_weeks_ago_across_the_government_classes(n):
    phrase = f"prieš {n} {unit_surface(n, 'week', accusative=True)}"
    assert start(phrase) == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n", [2, 3, 11, 20, 25, 45])
def test_minutes_ago_across_the_government_classes(n):
    phrase = f"prieš {n} {unit_surface(n, 'minute', accusative=True)}"
    assert start(phrase) == ad(ANCHOR - timedelta(minutes=n))


@pytest.mark.parametrize("n,form", [
    (1, "diena"), (2, "dienos"), (11, "dienų"), (21, "diena"), (30, "dienų"),
])
def test_nominative_surface_matches_the_rule(n, form):
    assert unit_surface(n, "day") == form


@pytest.mark.parametrize("n,form", [
    (1, "dieną"), (2, "dienas"), (11, "dienų"), (21, "dieną"), (30, "dienų"),
])
def test_accusative_surface_matches_the_rule(n, form):
    """The genitive plural is case-invariant, so it survives "prieš"
    unchanged while the singular and plural take the accusative."""
    assert unit_surface(n, "day", accusative=True) == form


@pytest.mark.parametrize("phrase,n", [
    ("prieš vieną dieną", 1),
    ("prieš dvi dienas", 2),
    ("prieš vienuolika dienų", 11),
    ("prieš dvidešimt vieną dieną", 21),
    ("prieš dvidešimt dvi dienas", 22),
    ("prieš trisdešimt vieną dieną", 31),
])
def test_spelled_numeral_governs_its_noun(phrase, n):
    assert start(phrase) == ad(ANCHOR - timedelta(days=n))
