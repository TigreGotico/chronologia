"""sv: the Scandinavian "<decade>-talet"/"-tallet" definite decade suffix.

"1990-talet" is the decade 1990-1999 -- the ten-year span
1990-01-01 .. 2000-01-01, NOT the single year 1990.  Gold is computed by
independent decade arithmetic (first year of the ten, first year of the
next ten), never read back from the parser.
"""
import pytest

from ._corpus import start_end, AstroDate


@pytest.mark.parametrize("dec", [1900, 1910, 1920, 1930, 1940, 1950,
                                 1960, 1970, 1980, 1990, 2000, 2010, 2020])
@pytest.mark.parametrize("suffix", ["talet", "tallet"])
def test_decade_talet_is_ten_years(dec, suffix):
    lo = dec - dec % 10
    assert start_end(f"{dec}-{suffix}") == (AstroDate(lo, 1, 1),
                                            AstroDate(lo + 10, 1, 1))
