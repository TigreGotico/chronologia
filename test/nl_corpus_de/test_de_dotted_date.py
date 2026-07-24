"""The dotted civil date in German: "15.06.2020".

DIN 5008 writes the everyday German date "15.06.2020", day first, and that
surface has to read as the day it names.  Reading only the year out of it
and stranding the day and the month in the remainder is a silent wrong:
the caller gets a confident whole-year span with nothing to tell it the
day was lost.

The adversarial half of this file is the other side of the same rule.  A dot
also separates a decimal fraction and, in these locales, a thousands group,
and it also ends an ordinal; none of those may turn into a date, and no input
may raise.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import parse, start_end, nomatch


def test_dotted_date_de():
    assert start_end("15.06.2020") == (AstroDate(2020, 6, 15),
                                       AstroDate(2020, 6, 16))


def test_dotted_date_in_a_sentence_de():
    s, e = start_end('das Treffen am 15.06.2020')
    assert (s, e) == (AstroDate(2020, 6, 15), AstroDate(2020, 6, 16))
    assert parse('das Treffen am 15.06.2020')[1] == 'das Treffen am'


def test_dotted_date_unpadded_de():
    """The leading zeros are optional; both forms read alike."""
    assert start_end('15.6.2020') == (AstroDate(2020, 6, 15),
                                      AstroDate(2020, 6, 16))


def test_dotted_date_day_over_twelve_de():
    """Day first, so the day may exceed twelve and the month may not."""
    assert start_end("31.12.1999") == (AstroDate(1999, 12, 31),
                                       AstroDate(2000, 1, 1))
    assert start_end("13.12.2024") == (AstroDate(2024, 12, 13),
                                       AstroDate(2024, 12, 14))


def test_dotted_date_two_digit_year_de():
    """A two-digit year goes through the same POSIX pivot the slashed form
    uses, so "15.06.20" is 2020 rather than 1920."""
    assert start_end("15.06.20") == (AstroDate(2020, 6, 15),
                                     AstroDate(2020, 6, 16))


@pytest.mark.parametrize("text,y,m,d", [('15. Juni 2020', 2020, 6, 15), ('3. Januar 2020', 2020, 1, 3)])
def test_written_date_still_reads_de(text, y, m, d):
    assert start_end(text) == (AstroDate(y, m, d), AstroDate(y, m, d + 1))


def test_a_thousands_group_is_not_a_date_de():
    """A thousands group carries one dot per group of three digits, never the
    two-dot day.month.year shape, so it can never read as a date."""
    r = parse('vor 1.000 Jahren')
    assert r is None or (r[0].start, r[0].end) != (AstroDate(2020, 6, 15),
                                                   AstroDate(2020, 6, 16))
    nomatch('1.000.000')


@pytest.mark.parametrize("text", [
    "1.2.3.4",          # a longer dotted run names no date at all
    "1.15.06.2020",     # ... and neither does its head
    "15.6.2020.5",
    "15..06.2020",      # an empty component
    "15.06.",           # no year
    "...",
    "0.0.0",            # day zero, month zero
    "99.99.9999",       # no such day, no such month
    "31.02.2020",       # February has no 31st, so nothing is fabricated
    "32.06.2020",
    "15.13.2020",       # month thirteen, and the day cannot be the month
])
def test_malformed_dotted_run_refuses_de(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "15.06.20201",      # a digit run that continues past the shape
    "15/06/20201",      # ... and the same run with the other separator
    "2024/03",          # a slashed year-month is not an ISO year-month
    "2026-071",
])
def test_a_broken_date_is_not_a_bare_year_de(text):
    """The all-or-nothing boundary guard the numeric literals carry, followed
    through to the answer.  A run like this binds no date, and the year inside
    it does not get to be read on its own either -- answering "2020" here would
    hand the caller a whole-year span with the day and the month silently gone.
    One rule for every separator: dot, slash and dash alike."""
    nomatch(text)


def test_trailing_sentence_dot_de():
    """A dot that ends the sentence is punctuation, not a fourth component."""
    assert start_end("15.06.2020.") == (AstroDate(2020, 6, 15),
                                        AstroDate(2020, 6, 16))


def test_dotted_date_with_a_clock_de():
    s, e = start_end('15.06.2020 um 14:30')
    assert s == AstroDate(2020, 6, 15, 14, 30)
    assert parse('15.06.2020 um 14:30')[1] == 'um'
