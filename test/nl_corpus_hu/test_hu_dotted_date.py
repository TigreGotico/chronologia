"""The dotted civil date in Hungarian: "2020.06.15".

Hungarian writes the numeric date year first with dots -- the Academy's
orthography (AkH. 297) and MSZ ISO 8601 agree on "2020.06.15" -- so the
surface is the ISO order with a different separator, and it resolves through
the same year-first path the dashed and slashed literals use.  A four-digit
lead is year-first in every language, so this needs no per-locale switch and
no day/month guess.

The spaced form the Academy prints in running text, "2020. június 3.", is
month-name vocabulary and reads through the ordinary written-date path; it is
here so the two never drift apart.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import parse, start_end, nomatch


def test_dotted_iso_date_hu():
    assert start_end("2020.06.15") == (AstroDate(2020, 6, 15),
                                       AstroDate(2020, 6, 16))


def test_dotted_iso_date_unpadded_hu():
    assert start_end("2020.6.15") == (AstroDate(2020, 6, 15),
                                      AstroDate(2020, 6, 16))


def test_dotted_iso_date_year_end_hu():
    assert start_end("1999.12.31") == (AstroDate(1999, 12, 31),
                                       AstroDate(2000, 1, 1))


def test_written_date_still_reads_hu():
    """The month-name form the Academy prints in running text."""
    assert start_end("2020. január 3.") == (AstroDate(2020, 1, 3),
                                            AstroDate(2020, 1, 4))


@pytest.mark.parametrize("text", [
    "2020.13.15",       # no thirteenth month, and year-first admits no swap
    "2020.06.31",       # June has no 31st, so nothing is fabricated
    "2020.00.15",
    "2020.06.",
    "1.2.3.4",
    "...",
])
def test_malformed_dotted_run_refuses_hu(text):
    nomatch(text)


def test_longer_digit_run_is_not_this_date_hu():
    """The all-or-nothing boundary guard the other numeric literals carry:
    "2020.06.155" is not 15 June with a spare digit, and "2020.06.15.5" is
    not 15 June with a spare fraction."""
    for text in ("2020.06.155", "2020.06.15.5"):
        r = parse(text)
        if r is not None:
            assert (r[0].start, r[0].end) != (AstroDate(2020, 6, 15),
                                              AstroDate(2020, 6, 16))


def test_a_thousands_group_is_not_a_date_hu():
    """Hungarian groups thousands with a space, but the dotted group other
    locales write must not read as a date here either."""
    nomatch("1.000.000")


def test_trailing_sentence_dot_hu():
    """Hungarian closes the date with a dot; it is punctuation, not a fourth
    component."""
    assert start_end("2020.06.15.") == (AstroDate(2020, 6, 15),
                                        AstroDate(2020, 6, 16))
