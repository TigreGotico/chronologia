"""Slovak eras: the secular "pred n. l." / "n. l." pair the academic
dictionary glosses under *letopočet*, its shorter variants "pr. n. l." and
"p. n. l.", and the Christian "pred Kr." / "po Kr." pair.
"""
import pytest

from ._corpus import parse, start, AstroDate


# -- BC: astronomical year numbering (44 BC == year -43) ------------------

@pytest.mark.parametrize("text,astro_year", [
    ("Caesara zavraždili v roku 44 pred n. l.", -43),
    ("Caesara zavraždili v roku 44 pr. n. l.", -43),
    ("Caesara zavraždili v roku 44 p. n. l.", -43),
    ("Rím bol založený v 753 pred naším letopočtom.", -752),
    ("Alexander zomrel v 323 pred kristom.", -322),
])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


# -- AD -------------------------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("Západorímska ríša padla v roku 476 n. l.", 476),
    ("Koncil zasadal v 325 nášho letopočtu.", 325),
    ("Konštantínopol bol založený v 330 po kr.", 330),
])
def test_ad(text, year):
    assert start(text) == AstroDate(year, 1, 1)


# -- a year without an era marker is an ordinary year ---------------------

def test_year_without_marker_stays_common_era():
    assert start("Stretnutie sa konalo v roku 1980.").year == 1980


# -- adversarial: nothing here may raise ----------------------------------

@pytest.mark.parametrize("text", [
    "Náš letopočet s tým nemá nič spoločné.",
    "pred naším letopočtom",
    "qwzx plkj mnbv",
    "",
])
def test_no_crash(text):
    parse(text)
