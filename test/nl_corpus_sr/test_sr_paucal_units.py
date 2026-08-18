"""Serbian numeral agreement: 1 nominative singular, 2-4 GENITIVE SINGULAR
(the paucal -- "dva sata", "tri dana"), 5+ genitive plural ("pet sati").
Compounds follow the modular Slavic rule off the LAST digit, with 11-14 the
standing exception that stays genitive plural despite ending in 1-4
("jedanaest dana", never the singular "jedanaest dan").

The gold is the rule itself, stated independently of the parser in
:func:`sr_form`; only the assembled phrase is handed to the extractor, in
both scripts.
"""
from datetime import timedelta

import pytest

from chronologia.extract.numfold_slavic import sr_lat2cyr

from ._corpus import ANCHOR, ad, start

#: (nominative singular, genitive singular / paucal, genitive plural)
_FORMS = {
    "hour": ("sat", "sata", "sati"),
    "day": ("dan", "dana", "dana"),
    "minute": ("minut", "minuta", "minuta"),
    "week": ("sedmica", "sedmice", "sedmica"),
    "year": ("godina", "godine", "godina"),
}


def sr_form(n: int, kind: str) -> str:
    sg, pauc, plu = _FORMS[kind]
    last2, last1 = n % 100, n % 10
    if last2 in (11, 12, 13, 14):
        return plu
    if last1 == 1:
        return sg
    if last1 in (2, 3, 4):
        return pauc
    return plu


def _delta(n, kind):
    return {"hour": timedelta(hours=n), "day": timedelta(days=n),
            "minute": timedelta(minutes=n), "week": timedelta(weeks=n),
            "year": timedelta(days=365 * n)}[kind]


@pytest.mark.parametrize("n,kind,expected", [
    (1, "hour", "sat"), (2, "hour", "sata"), (4, "hour", "sata"),
    (5, "hour", "sati"), (11, "hour", "sati"), (21, "hour", "sat"),
    (24, "hour", "sata"), (25, "hour", "sati"),
])
def test_sr_form_matches_the_rule(n, kind, expected):
    assert sr_form(n, kind) == expected


@pytest.mark.parametrize("n", [1, 2, 4, 5, 11, 21, 24, 25])
def test_hours_ago_boundary_cases_latin(n):
    phrase = f"pre {n} {sr_form(n, 'hour')}"
    assert start(phrase) == ad(ANCHOR - timedelta(hours=n))


@pytest.mark.parametrize("n", [1, 2, 4, 5, 11, 21, 24, 25])
def test_hours_ago_boundary_cases_cyrillic(n):
    phrase = f"{sr_lat2cyr('pre')} {n} {sr_lat2cyr(sr_form(n, 'hour'))}"
    assert start(phrase) == ad(ANCHOR - timedelta(hours=n))


@pytest.mark.parametrize("n", [1, 2, 4, 5, 11, 21, 24, 25])
def test_days_ago_boundary_cases_latin(n):
    phrase = f"pre {n} {sr_form(n, 'day')}"
    assert start(phrase) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n", [1, 2, 4, 5, 11, 21, 24, 25])
def test_days_ago_boundary_cases_cyrillic(n):
    phrase = f"{sr_lat2cyr('pre')} {n} {sr_lat2cyr(sr_form(n, 'day'))}"
    assert start(phrase) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n", [1, 2, 4, 5, 11, 21])
def test_minutes_ago_boundary_cases(n):
    phrase = f"pre {n} {sr_form(n, 'minute')}"
    assert start(phrase) == ad(ANCHOR - timedelta(minutes=n))


@pytest.mark.parametrize("n", [1, 2, 4, 5, 11, 21])
def test_weeks_ago_boundary_cases(n):
    phrase = f"pre {n} {sr_form(n, 'week')}"
    assert start(phrase) == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n", [1, 2, 4, 5, 21])
def test_hours_from_now_boundary_cases(n):
    phrase = f"za {n} {sr_form(n, 'hour')}"
    assert start(phrase) == ad(ANCHOR + timedelta(hours=n))


def test_dva_sata_is_not_pet_sati():
    """Adversarial: the paucal ("dva sata") and the genitive plural
    ("pet sati") are different surfaces and must not resolve to the same
    offset."""
    two = start("pre dva sata")
    five = start("pre pet sati")
    assert two != five
    assert two == ad(ANCHOR - timedelta(hours=2))
    assert five == ad(ANCHOR - timedelta(hours=5))


def test_eleven_is_the_standing_exception():
    """"jedanaest" ends in 1 but is NOT nominative singular -- it takes the
    genitive plural, the paucal's own boundary exception."""
    assert sr_form(11, "day") == "dana"
    assert start("pre jedanaest dana") == ad(ANCHOR - timedelta(days=11))
