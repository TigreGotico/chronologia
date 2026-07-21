"""German spoken decades ("die zwanziger Jahre") and localized ranges
("von A bis B", "zwischen A und B") -- the range connectives resolve from
the locale's own from/to/between/and connectors, no English words involved.
"""
import pytest

from ._corpus import start, start_end, span, nomatch, AstroDate


# -- spoken decades -------------------------------------------------------

@pytest.mark.parametrize("text,y0", [
    ("die zwanziger jahre", 1920), ("die dreißiger jahre", 1930),
    ("die vierziger jahre", 1940), ("die fünfziger jahre", 1950),
    ("die sechziger jahre", 1960), ("die siebziger jahre", 1970),
    ("die achtziger jahre", 1980), ("die neunziger jahre", 1990),
    ("die zwanziger", 1920), ("die achtziger", 1980),
])
def test_decade(text, y0):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y0 + 10, 1, 1))


# -- ranges "von A bis B" -------------------------------------------------

def test_range_von_bis_days():
    assert start_end("von 5. juni bis 12. juni") == (
        AstroDate(2018, 6, 5), AstroDate(2018, 6, 13))


def test_range_bare_bis():
    # no "von": bare "A bis B" still reads as a range
    assert start_end("5. juni bis 12. juni") == (
        AstroDate(2018, 6, 5), AstroDate(2018, 6, 13))


def test_range_months():
    s, e = start_end("von märz 2020 bis juni 2020")
    assert s == AstroDate(2020, 3, 1)
    assert e == AstroDate(2020, 7, 1)


# -- ranges "zwischen A und B" --------------------------------------------

def test_range_zwischen_und():
    s, e = start_end("zwischen juni und august 2020")
    assert s == AstroDate(2017, 6, 1)     # bare left month -> anchor year
    assert e == AstroDate(2020, 9, 1)


def test_range_years():
    # range end is the END of the right endpoint's year (all of 2000)
    assert start_end("von 1990 bis 2000") == (
        AstroDate(1990, 1, 1), AstroDate(2001, 1, 1))


# -- clock range crossing midnight rolls a day ----------------------------

def test_clock_range_wraps():
    s, e = start_end("von 22 uhr bis 2 uhr")
    assert s.hour == 22
    assert e.day == s.day + 1 and e.hour == 2


# -- adversarial: "halb neun" is a clock, never a "halb ... " range -------

def test_halb_is_not_a_range():
    assert span("halb neun").width.total_seconds() == 60
