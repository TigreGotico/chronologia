"""Polish eras: "p.n.e." (przed naszą erą) and "n.e." (naszej ery), the
spellings the Wielki słownik ortograficzny records, written after the year.
The spaced variant is read as well, since it turns up in typeset prose.
"""
import pytest

from ._corpus import parse, start, AstroDate


# -- BC: astronomical year numbering (44 BC == year -43) ------------------

@pytest.mark.parametrize("text,astro_year", [
    ("Cezar zginął w 44 p.n.e.", -43),
    ("Cezar zginął w 44 p. n. e.", -43),
    ("Rzym założono w 753 przed naszą erą.", -752),
])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


# -- AD -------------------------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("Cesarstwo zachodniorzymskie upadło w 476 n.e.", 476),
    ("Mieszko I przyjął chrzest w 966 n. e.", 966),
    ("Sobór obradował w 325 naszej ery.", 325),
])
def test_ad(text, year):
    assert start(text) == AstroDate(year, 1, 1)


# -- a year without an era marker is an ordinary year ---------------------

def test_year_without_marker_stays_common_era():
    assert start("Spotkanie odbyło się w 1980 roku.").year == 1980


# -- adversarial: nothing here may raise ----------------------------------

@pytest.mark.parametrize("text", [
    "Nasza era nie ma z tym nic wspólnego.",
    "przed naszą erą",
    "qwzx plkj mnbv",
    "",
])
def test_no_crash(text):
    parse(text)
