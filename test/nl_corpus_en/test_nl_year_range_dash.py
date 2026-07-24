"""The written year range: "1914-1918".

A hyphen between two four-digit years is how prose sets a span of years, and
it means exactly what "from 1914 to 1918" means -- the whole of both endpoint
years, so 1914-01-01 up to 1919-01-01.  The hyphenated form used to be refused
outright, because the ISO year-month literal ate "1914-19" and then found no
month 19.

The tight hyphen is trusted only between two four-digit numbers.  Every other
hyphenated numeric shape a date wears is lexed as a single token long before
range detection runs -- an ISO date, an ISO year-month, a numeric date, an ISO
week -- and no calendar component but a year is written with four digits.  So
"12-15" is not a range, and "2026-07" is still a month.
"""
import pytest

from ._corpus import AstroDate, start_end, nomatch, parse


@pytest.mark.parametrize("text,s,e", [
    ("1914-1918", (1914, 1, 1), (1919, 1, 1)),
    ("1939-1945", (1939, 1, 1), (1946, 1, 1)),
    ("1914–1918", (1914, 1, 1), (1919, 1, 1)),     # en dash, as typeset prose sets it
    ("1914—1918", (1914, 1, 1), (1919, 1, 1)),     # em dash
    ("2020-2021", (2020, 1, 1), (2022, 1, 1)),
    ("1999-2000", (1999, 1, 1), (2001, 1, 1)),     # across the millennium boundary
])
def test_written_year_range(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


def test_hyphen_reads_as_the_spelled_range_does():
    """The hyphen is only punctuation for "from ... to ...", so the two
    surfaces must resolve to the identical span."""
    assert start_end("1914-1918") == start_end("from 1914 to 1918")


def test_range_inside_a_sentence():
    s, e = start_end("World War I (1914-1918) reshaped Europe")
    assert (s, e) == (AstroDate(1914, 1, 1), AstroDate(1919, 1, 1))


def test_reversed_endpoints_do_not_fabricate_a_span():
    """"1918-1914" runs backwards and names no span; the parser falls back to
    reading the leading year rather than inventing a reversed one."""
    s, e = start_end("1918-1914")
    assert (s, e) == (AstroDate(1918, 1, 1), AstroDate(1919, 1, 1))
    assert e > s


@pytest.mark.parametrize("text,s,e", [
    ("2026-07-24", (2026, 7, 24), (2026, 7, 25)),   # still an ISO date
    ("2026-07", (2026, 7, 1), (2026, 8, 1)),        # still an ISO year-month
    ("5-6-24", (2024, 5, 6), (2024, 5, 7)),         # still a numeric date (mdy here)
])
def test_hyphenated_date_literals_are_untouched(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text", ["12-15", "3-7", "99-100"])
def test_non_year_hyphen_pairs_are_not_ranges(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["-", "----", "1914-", "-1918", "--1914--"])
def test_degenerate_hyphens_never_raise(text):
    parse(text)
