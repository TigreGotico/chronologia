"""Estonian adversarial cases: non-temporal text, bare fragments and case-form
near-misses.  Every case asserts a clean outcome so the parser stays
conservative.
"""
import pytest

from ._corpus import nomatch, span


@pytest.mark.parametrize("text", [
    "söön iga hommik õuna",
    "kass magab",
    "tere hommikust",
    "ilus raamat",
    "lähme kinno",
    "laud on puust",
    "prügi",
    "selge",
    "suur tänu",
    "roheline hobune",
])
def test_non_temporal_nomatch(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "kakskümmend kolm",
    "mõni",
    "tund",
    "minut",
    "pärast",
    "tagasi",
    "pool",
])
def test_bare_fragment_nomatch(text):
    nomatch(text)


@pytest.mark.parametrize("text,mo", [
    ("jaanuar", 1),
    ("juuni", 6),
    ("detsember", 12),
])
def test_bare_month_resolves(text, mo):
    assert span(text).start.month == mo


@pytest.mark.parametrize("text,mo", [
    ("juunis", 6),
    ("detsembris", 12),
])
def test_inessive_month_resolves(text, mo):
    # the inessive "juunis" (in June) still binds the June surface
    assert span(text).start.month == mo


def test_genitive_number_needs_a_unit():
    # "kahe" (of two) alone, with no unit or marker, must not parse
    nomatch("kahe")
