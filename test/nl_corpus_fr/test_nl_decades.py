"""French decade references.

"Les années 1980" and "les années 80" name the ten years 1980-1989, not the
single year 1980: the plural "années" in front of a whole ten is the French
decade frame (Portail linguistique du Canada, "Les années quatre-vingt ou
quatre-vingts?": "la série d'années comprises entre 1980 et 1989").  The same
frame in front of digits that are *not* a whole ten introduces an ordinary run
of years ("les années 1914-1918"), which is why the numeral must name a decade
before the decade reading applies.  The scoped-century form ("le 20e siècle")
is the 100-year span and lives in the ranges corpus.
"""
from datetime import timedelta

import pytest

from ._corpus import span, start, start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,y0", [
    ("les années 1980", 1980),
    ("les années 1990", 1990),
    ("les années 1920", 1920),
    ("les années 80", 1980),
    ("les années 90", 1990),
    ("dans les années 1970", 1970),
])
def test_decade(text, y0):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y0 + 10, 1, 1))


def test_decade_is_ten_years_wide():
    assert span("les années 1980").width == timedelta(days=3653)


def test_bare_year_is_still_a_year():
    # no plural frame, so "en 1980" stays the single year it names
    assert start_end("en 1980") == (AstroDate(1980, 1, 1),
                                    AstroDate(1981, 1, 1))


def test_year_run_is_not_a_decade():
    # "les années 1914-1918" are the war years: the frame is the same, but
    # 1914 opens no decade, so the range reading stands
    assert start_end("les années 1914-1918") == (AstroDate(1914, 1, 1),
                                                 AstroDate(1919, 1, 1))


def test_garbage_does_not_raise():
    nomatch("les années ???")


def test_bare_spelled_clock():
    # dev's SCOPE_UNIT hour-exclusion lets a bare spelled clock ("trois
    # heures") read as 3 o'clock instead of colliding with the scoped
    # "Nth hour" ordinal reading.
    assert start("trois heures") == AstroDate(2017, 6, 28, 3, 0)
