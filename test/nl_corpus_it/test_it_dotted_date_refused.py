"""Italian does not write the dotted date, so it reads as nothing.

The continental "15.06.2020" is the official civil form of German, Russian,
Polish, Czech, Finnish, Turkish and Dutch, and the parser reads it there.
Italian writes the numeric date with slashes, so the dotted surface is not a
Italian date and must not be read as one.

Refusing to read it is only half the rule.  The engine used to answer such a
string with the bare year and leave "15.06" in the remainder -- a confident
whole-year span with nothing to tell the caller that the day and the month had
been dropped.  A numeral visibly glued into a date-shaped run does not get to
be read as a lone year just because the run was rejected, so the honest answer
is nothing at all.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch


@pytest.mark.parametrize("text", [
    "15.06.2020",
    "06.15.2020",
    "15.6.2020",
    'il 15.06.2020',
])
def test_dotted_date_refused_it(text):
    nomatch(text)


def test_the_slashed_date_still_reads_it():
    """The numeric date Italian does write is untouched."""
    assert start_end("15/06/2020") == (AstroDate(2020, 6, 15),
                                       AstroDate(2020, 6, 16))


def test_year_first_dots_still_read_it():
    """A four-digit lead is year-first in every language, dots included."""
    assert start_end("2020.06.15") == (AstroDate(2020, 6, 15),
                                       AstroDate(2020, 6, 16))


def test_the_written_year_range_survives_it():
    """The one glued shape that is not a broken date: a tight hyphen between
    two four-digit years, where neither side can be a day or a month."""
    assert start_end("1914-1918") == (AstroDate(1914, 1, 1),
                                      AstroDate(1919, 1, 1))
