"""French eras and deep time: BC/AD ("avant/après Jésus-Christ",
"av./ap. J.-C."), the "l'an" year reference, and "il y a N millions/
milliards d'années" deep-time offsets.

Astronomical year numbering: 44 BC == year -43.  Deep time is reckoned
before the 1950 radiocarbon present.
"""
import pytest

from ._corpus import span, start, nomatch, AstroDate

_BP_EPOCH = 1950


# -- BC / AD --------------------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("44 av. j.-c.", -43),
    ("44 avant jésus-christ", -43),
    ("44 avant notre ère", -43),
    ("753 av. j.-c.", -752),
    ("2020 après jésus-christ", 2020),
    ("2020 de notre ère", 2020),
])
def test_era_year(text, year):
    assert start(text).year == year


def test_bc_is_year_wide():
    s = span("44 av. j.-c.")
    assert s.end.year - s.start.year == 1


# -- l'an year reference --------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("l'an 2000", 2000),
    ("en l'an 1789", 1789),
])
def test_year_reference(text, year):
    assert start(text).year == year


# -- deep time (il y a N millions/milliards d'années) ---------------------

@pytest.mark.parametrize("text,years_ago", [
    ("il y a 66 millions d'années", 66_000_000),
    ("il y a 4 milliards d'années", 4_000_000_000),
    ("il y a 250 millions d'années", 250_000_000),
])
def test_deep_time(text, years_ago):
    assert start(text).year == _BP_EPOCH - years_ago


# -- adversarial ----------------------------------------------------------

def test_two_digit_year_is_not_a_year_reference():
    nomatch("en l'an 44")   # bare year reference needs >= 4 digits


def test_deep_time_needs_marker():
    # a bare "66 millions d'années" without "il y a" is not deep time
    nomatch("66 millions d'années")
