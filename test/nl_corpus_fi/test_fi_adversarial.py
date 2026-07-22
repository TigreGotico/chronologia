"""Finnish adversarial cases: non-temporal text, bare fragments and case-form
near-misses.  Every case asserts a clean outcome so the parser stays
conservative.
"""
import pytest

from ._corpus import nomatch, span


@pytest.mark.parametrize("text", [
    "syön omenoita joka aamu",
    "kissa nukkuu",
    "hyvää huomenta",
    "kaunis kirja",
    "mennään elokuviin",
    "pöytä on puuta",
    "roskaa",
    "selvä",
    "kiitos paljon",
    "vihreä hevonen",
])
def test_non_temporal_nomatch(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "kaksikymmentäkolme",
    "muutama",
    "tunti",
    "minuutti",
    "kuluttua",
    "sitten",
    "puoli",
])
def test_bare_fragment_nomatch(text):
    nomatch(text)


@pytest.mark.parametrize("text,mo", [
    ("tammikuu", 1),
    ("kesäkuu", 6),
    ("joulukuu", 12),
])
def test_bare_month_resolves(text, mo):
    assert span(text).start.month == mo


@pytest.mark.parametrize("text,mo", [
    ("kesäkuussa", 6),
    ("joulukuussa", 12),
])
def test_inessive_month_resolves(text, mo):
    # the inessive "kesäkuussa" (in June) still binds the June surface
    assert span(text).start.month == mo


def test_genitive_number_needs_a_unit():
    # "kahden" (of two) alone, with no unit or marker, must not parse
    nomatch("kahden")
