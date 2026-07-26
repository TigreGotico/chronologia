"""The dotted civil date in Slovak: "15.06.2020" and the spaced "15. 6. 2020".

STN 01 6910 (the Slovak counterpart of the Czech CSN) writes the everyday
date day first with dots, and in running text with a space after each dot,
"15. 6. 2020".  Either surface has to read as the day it names.  Reading only
the year out of it and stranding the day and the month in the remainder is a
silent wrong: the caller gets a confident whole-year span with nothing to tell
it the day was lost.

The adversarial half of this file is the other side of the same rule.  A dot
also separates a decimal fraction and, in these locales, a thousands group,
and it also ends an ordinal; none of those may turn into a date.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import parse, start_end, nomatch


def test_dotted_date_sk():
    assert start_end("15.06.2020") == (AstroDate(2020, 6, 15),
                                       AstroDate(2020, 6, 16))


def test_dotted_date_unpadded_sk():
    """The leading zeros are optional; both forms read alike."""
    assert start_end('15.6.2020') == (AstroDate(2020, 6, 15),
                                      AstroDate(2020, 6, 16))


@pytest.mark.parametrize("text", ["15. 6. 2020", "15. 06. 2020"])
def test_dotted_date_spaced_sk(text):
    """STN 01 6910 writes the everyday date with a space after each dot,
    "15. 6. 2020"; the spaced surface names the same day and must not strand
    the day-and-month while returning the bare year."""
    assert start_end(text) == (AstroDate(2020, 6, 15), AstroDate(2020, 6, 16))


def test_dotted_date_spaced_in_a_sentence_sk():
    s, e = start_end('stretnutie 15. 6. 2020')
    assert (s, e) == (AstroDate(2020, 6, 15), AstroDate(2020, 6, 16))
    assert parse('stretnutie 15. 6. 2020')[1] == 'stretnutie'


def test_spaced_pair_without_a_year_is_not_a_date_sk():
    """"15. 6." is two ordinals, not a date: with no four-digit year to
    anchor the pattern nothing may be fabricated."""
    nomatch("15. 6.")


@pytest.mark.parametrize("text", [
    "1.2.3.4",
    "15.06.",           # no year
    "31.02.2020",       # February has no 31st
    "15.13.2020",       # month thirteen
])
def test_malformed_dotted_run_refuses_sk(text):
    nomatch(text)
