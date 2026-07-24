"""English has no dotted numeric date, so dots stay numbers.

The continental "15.06.2020" is the official civil form of German, Russian,
Polish, Czech, Finnish, Turkish, Dutch and their neighbours, and the parser
reads it there.  English writes the numeric date with slashes, month first,
and writes nothing with dots in either order -- so an English caller who
types dots has not written a date, and the parser must not invent one for
them.  The dotted literal is therefore a per-language tokenizer mode, and
this file is the proof that English does not have it.

Not reading it is only half the rule.  The engine used to answer such a string
with the bare year and leave "06.15" in the remainder, which told the caller a
whole year had been asked for when a day had been.  A numeral visibly glued
into a date-shaped run does not get to be read as a lone year just because the
run was rejected, whatever the separator, so these refuse outright.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import parse, start_end, nomatch


@pytest.mark.parametrize("text", ["06.15.2020", "15.06.2020", "15.6.2020"])
def test_dots_are_not_a_date_in_english(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "2024/03",          # a slashed year-month is not an ISO year-month
    "2026-071",         # a digit run continuing past the ISO year-month
    "2026-07-244",
    "12/11/20244",
    "06/15/20201",
])
def test_a_broken_date_is_not_a_bare_year_in_english(text):
    """One rule for every separator: dot, slash and dash alike."""
    nomatch(text)


@pytest.mark.parametrize("text,y", [("1914-1918", 1914), ("2020-2021", 2020)])
def test_the_written_year_range_survives(text, y):
    """The one glued shape that is not a broken date: a tight hyphen between
    two four-digit numbers, where neither side can be a day or a month."""
    assert start_end(text)[0] == AstroDate(y, 1, 1)


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
