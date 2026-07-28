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


# -- digit decades ("die 1980er Jahre") -----------------------------------
#
# Duden glosses "Achtzigerjahre" (in digits "80er-Jahre"/"80er Jahre") as
# "die Jahre 80 bis 89 eines bestimmten Jahrhunderts umfassendes Jahrzehnt",
# so the -er ending on the numeral names the ten-year span, not the year the
# digits spell.

@pytest.mark.parametrize("text,y0", [
    ("die 1980er", 1980), ("die 1980er jahre", 1980),
    ("die 1990er jahre", 1990), ("die 1920er jahre", 1920),
    ("in den 1970er jahren", 1970), ("die 80er jahre", 1980),
])
def test_digit_decade(text, y0):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y0 + 10, 1, 1))


def test_bare_year_is_still_a_year():
    # without the -er ending the digits stay the single year they spell
    assert start_end("im jahr 1980") == (AstroDate(1980, 1, 1),
                                         AstroDate(1981, 1, 1))


def test_decade_garbage_ending_is_no_decade():
    # a bogus ending is not the -er of a decade: the digits fall back to the
    # plain year and the junk lands in the remainder rather than raising
    assert start_end("die 1980xy ???") == (AstroDate(1980, 1, 1),
                                           AstroDate(1981, 1, 1))
    nomatch("xyz ???")


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
    assert s == AstroDate(2020, 6, 1)     # bare left month borrows the trailing year (2020)
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
