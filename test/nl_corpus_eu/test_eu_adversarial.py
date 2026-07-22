"""Basque adversarial cases: non-temporal text, bare fragments, and
case-form near-misses on the inflected date words.  Every case asserts a
clean outcome so the parser stays conservative.
"""
import pytest

from ._corpus import nomatch, span, start, ad
from datetime import datetime


@pytest.mark.parametrize("text", [
    "sagarrak jaten ditut goizero",
    "katua lo dago",
    "egun on",
    "liburu eder bat",
    "zinera goaz",
    "mahaia egurrezkoa da",
    "zaborra",
    "ados",
    "eskerrik asko",
    "zaldi berdea",
])
def test_non_temporal_nomatch(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "hogeita hiru",
    "batzuk",
    "ordu",
    "minutu",
    "barru",
    "duela",
    "erdi",
])
def test_bare_fragment_nomatch(text):
    nomatch(text)


@pytest.mark.parametrize("text,mo", [
    ("ekaina", 6),
    ("abendua", 12),
    ("urtarrila", 1),
])
def test_bare_month_resolves(text, mo):
    assert span(text).start.month == mo


@pytest.mark.parametrize("text,mo", [
    ("ekainaren", 6),
    ("abenduaren", 12),
])
def test_genitive_month_resolves(text, mo):
    # the genitive "ekainaren" (of June) still binds the June surface
    assert span(text).start.month == mo


def test_year_relational_suffix_strips():
    # "2020ko" (of 2020) folds to the plain year and resolves to the month
    assert start("2020ko ekainaren 5ean") == ad(datetime(2020, 6, 5))


def test_inessive_day_suffix_strips():
    # "5ean" (on the 5th) folds to the day 5, not a stray token
    assert start("ekainaren 5ean").day == 5
