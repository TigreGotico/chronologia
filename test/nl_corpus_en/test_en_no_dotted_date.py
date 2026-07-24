"""English has no dotted numeric date, so dots stay numbers.

The continental "15.06.2020" is the official civil form of German, Russian,
Polish, Czech, Finnish, Turkish, Dutch and their neighbours, and the parser
reads it there.  English writes the numeric date with slashes, month first,
and writes nothing with dots in either order -- so an English caller who
types dots has not written a date, and the parser must not invent one for
them.  The dotted literal is therefore a per-language tokenizer mode, and
this file is the proof that English does not have it.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import parse, start_end


@pytest.mark.parametrize("text", ["06.15.2020", "15.06.2020", "15.6.2020"])
def test_dots_are_not_a_date_in_english(text):
    r = parse(text)
    if r is not None:
        assert (r[0].start, r[0].end) != (AstroDate(2020, 6, 15),
                                          AstroDate(2020, 6, 16))


def test_the_slashed_date_is_month_first_in_english():
    """The English numeric date is unchanged: slashes, month first."""
    assert start_end("06/15/2020") == (AstroDate(2020, 6, 15),
                                       AstroDate(2020, 6, 16))


def test_year_first_dots_still_read_in_english():
    """A four-digit lead is year-first in every language, dots included, so
    the ISO literal is language-neutral the way the dashed form always was."""
    assert start_end("2020.06.15") == (AstroDate(2020, 6, 15),
                                       AstroDate(2020, 6, 16))


def test_a_decimal_is_still_a_number_in_english():
    r = parse("in 2.5 days")
    assert r is not None and r[1] == ""
