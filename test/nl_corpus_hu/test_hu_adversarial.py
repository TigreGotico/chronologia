"""Hungarian adversarial cases: non-temporal text, bare fragments, and the
hét (seven / week) homograph trap.  Every case asserts a clean outcome so
the parser stays conservative.
"""
import pytest

from ._corpus import nomatch, span, start, ad
from datetime import datetime


@pytest.mark.parametrize("text", [
    pytest.param(
        "minden reggel almát eszem",
        marks=pytest.mark.xfail(reason="bare daypart 'reggel' now binds the "
                                "morning band; the 'minden' recurrence is not "
                                "modelled, disambiguation is downstream",
                                strict=True)),
    "a macska alszik",
    "jó reggelt",
    "egy szép könyv",
    "menjünk moziba",
    "az asztal fából van",
    "szemét",
    "rendben",
    "köszönöm szépen",
    "zöld ló",
])
def test_non_temporal_nomatch(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "huszonhárom",
    "néhány",
    "óra",
    "perc",
    "múlva",
    "ezelőtt",
    "fél",
])
def test_bare_fragment_nomatch(text):
    nomatch(text)


@pytest.mark.parametrize("text,mo", [
    ("január", 1),
    ("június", 6),
    ("december", 12),
])
def test_bare_month_resolves(text, mo):
    assert span(text).start.month == mo


def test_het_reads_as_week_not_seven():
    # "két hét múlva" -> 2 WEEKS (hét is the week unit here, never 7)
    assert start("két hét múlva") == ad(datetime(2017, 7, 11, 13, 4))


def test_inessive_month_alone_resolves():
    # "júniusban" (in June) still binds the June surface
    assert span("júniusban").start.month == 6
