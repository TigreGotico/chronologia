# -*- coding: utf-8 -*-
"""Spelled ordinals above the tenth (11th-31st) fold to ORD for French -- R95.

French spells its 11th-19th/21st-29th/31st ordinals as compounds built on
"ième" ("onzième" = eleventh, "vingt et unième" = twenty-first) that the
shared ``ovos_number_parser`` French back-end does not recognise as ordinals
at all: it reads the "ième" suffix as a *fraction* marker instead ("onzième"
-> 1/11 = 0.0909...), so every one of these compounds was absent from the
number fold's word set entirely.  A sentence built on one never tokenized an
ordinal at all: "le treizième mois de 2026" silently degraded to a bare
year_ref match on "2026" (span = the whole year, remainder = "le treizième
mois de" stranded) instead of refusing outright the way the digit ordinal
("le 13e mois de 2026") and the fused-compound Spanish/Italian ordinals
already do (R87/R91).

Forms and their citation: Larousse / Académie française, "Les adjectifs
numéraux ordinaux" -- 11th-16th are irregular fused words (onze -> onzième,
etc.); 17th-19th and 21st-29th prefix the ten ("dix-septième",
"vingt-deuxième"); the X1 forms insert the coordinator "et" before "unième"
rather than hyphenating ("vingt et unième", "trente et unième"), exactly as
the cardinals themselves do ("vingt et un").

Golds are computed by independent calendar reasoning (month/day mapped by
hand from the cited ordinal value), never read back from the parser.
"""
import pytest

from ._corpus import start, nomatch


@pytest.mark.parametrize("text,mo", [
    # only 11th and 12th are valid MONTH ordinals
    ("le onzième mois de 2026", 11),
    ("le douzième mois de 2026", 12),
])
def test_teen_ordinal_valid_month(text, mo):
    s = start(text)
    assert (s.year, s.month) == (2026, mo)
    assert s.day == 1


@pytest.mark.parametrize("text", [
    # the exact live bug report: 13th month does not exist -- must refuse,
    # never silently fall back to the bare year
    "le treizième mois de 2026",
    # every other spelled ordinal 14th-19th, 21st-31st: all impossible as a
    # month
    "le quatorzième mois de 2026",
    "le quinzième mois de 2026",
    "le seizième mois de 2026",
    "le dix-septième mois de 2026",
    "le dix-huitième mois de 2026",
    "le dix-neuvième mois de 2026",
    "le vingtième mois de 2026",
    "le vingt et unième mois de 2026",
    "le vingt-deuxième mois de 2026",
    "le vingt-troisième mois de 2026",
    "le vingt-quatrième mois de 2026",
    "le vingt-cinquième mois de 2026",
    "le vingt-sixième mois de 2026",
    "le vingt-septième mois de 2026",
    "le vingt-huitième mois de 2026",
    "le vingt-neuvième mois de 2026",
    "le trentième mois de 2026",
    "le trente et unième mois de 2026",
])
def test_teen_ordinal_impossible_month_refuses(text):
    nomatch(text)


def test_no_silent_year_fallback_regression():
    """The exact regression this fix closes: a spelled teen ordinal must not
    leave the parser matching only the bare trailing year with the ordinal
    phrase stranded in the remainder."""
    from ._corpus import parse
    r = parse("le treizième mois de 2026")
    assert r is None, (
        f"'le treizième mois de 2026' must refuse (None); the pre-fix "
        f"defect silently matched the bare year 2026, got {r!r}")


def test_scoped_ordinal_day_of_month():
    """A day-of-month scoped ordinal built on a spelled 21st -- the digit
    form ("le 21e jour de janvier") already resolves; the spelled form must
    match it exactly."""
    s = start("le vingt et unième jour de janvier")
    assert (s.month, s.day) == (1, 21)


@pytest.mark.parametrize("text,mo", [
    # controls: ordinals already inside the fold's vocabulary (1st, 3rd)
    # must be unaffected by the new compound table.
    ("le premier mois de 2026", 1),
    ("le troisième mois de 2026", 3),
])
def test_low_ordinal_controls_unchanged(text, mo):
    s = start(text)
    assert (s.year, s.month) == (2026, mo)
