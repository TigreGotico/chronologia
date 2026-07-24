"""Czech eras: the secular "př. n. l." / "n. l." pair and the Christian
"př. Kr." / "po Kr." pair, both written after the year.  The unspaced
variants are read too, because that is how the abbreviations are typed.
"""
import pytest

from ._corpus import parse, start, AstroDate


# -- BC: astronomical year numbering (44 BC == year -43) ------------------

@pytest.mark.parametrize("text,astro_year", [
    ("Caesar byl zavražděn v roce 44 př. n. l.", -43),
    ("Caesar byl zavražděn v roce 44 př.n.l.", -43),
    ("Řím byl založen v 753 před naším letopočtem.", -752),
    ("Parthenón byl dokončen v 432 př. kr.", -431),
    ("Alexandr zemřel v 323 před kristem.", -322),
])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


# -- AD -------------------------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("Západořímská říše padla v roce 476 n. l.", 476),
    ("Západořímská říše padla v roce 476 n.l.", 476),
    ("Koncil zasedal v 325 našeho letopočtu.", 325),
    ("Konstantinopol byla založena v 330 po kr.", 330),
])
def test_ad(text, year):
    assert start(text) == AstroDate(year, 1, 1)


# -- a year without an era marker is an ordinary year ---------------------

def test_year_without_marker_stays_common_era():
    assert start("Schůzka proběhla v roce 1980.").year == 1980


# -- adversarial: nothing here may raise ----------------------------------

@pytest.mark.parametrize("text", [
    "Náš letopočet s tím nemá nic společného.",
    "před naším letopočtem",
    "qwzx plkj mnbv",
    "",
])
def test_no_crash(text):
    parse(text)
