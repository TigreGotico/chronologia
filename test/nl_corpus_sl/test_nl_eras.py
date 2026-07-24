"""Slovene eras: "pr. n. št." (pred našim štetjem) and "n. št." / "po n. št."
(našega štetja), the abbreviations the spelling guide records.  Only this
secular pair is shipped, because it is the pair with a citable authority.
"""
import pytest

from ._corpus import parse, start, AstroDate


# -- BC: astronomical year numbering (44 BC == year -43) ------------------

@pytest.mark.parametrize("text,astro_year", [
    ("Cezarja so umorili leta 44 pr. n. št.", -43),
    ("Cezarja so umorili leta 44 pr.n.št.", -43),
    ("Rim je bil ustanovljen 753 pred našim štetjem.", -752),
])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


# -- AD -------------------------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("Zahodno rimsko cesarstvo je propadlo 476 n. št.", 476),
    ("Koncil je zasedal 325 po n. št.", 325),
    ("Carigrad je bil ustanovljen 330 našega štetja.", 330),
])
def test_ad(text, year):
    assert start(text) == AstroDate(year, 1, 1)


# -- a year without an era marker is an ordinary year ---------------------

def test_year_without_marker_stays_common_era():
    assert start("Srečanje je bilo leta 1980.").year == 1980


# -- adversarial: nothing here may raise ----------------------------------

@pytest.mark.parametrize("text", [
    "Naše štetje s tem nima nič opraviti.",
    "pred našim štetjem",
    "qwzx plkj mnbv",
    "",
])
def test_no_crash(text):
    parse(text)
