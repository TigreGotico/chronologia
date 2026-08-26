"""Calendar dates: day before month, and the two month registers CLDR gives."""
import pytest

from ._corpus import day, nomatch, parse, span, start_end


MONTHS = [
    ("Januari", "Jan", 1), ("Februari", "Feb", 2), ("Machi", "Mac", 3),
    ("Aprili", "Apr", 4), ("Mei", "Mei", 5), ("Juni", "Jun", 6),
    ("Julai", "Jul", 7), ("Agosti", "Ago", 8), ("Septemba", "Sep", 9),
    ("Oktoba", "Okt", 10), ("Novemba", "Nov", 11), ("Desemba", "Des", 12),
]


@pytest.mark.parametrize("wide,abbr,n", MONTHS)
def test_the_wide_month_name_reads(wide, abbr, n):
    assert start_end(f"15 {wide} 2027") == day(2027, n, 15)


@pytest.mark.parametrize("wide,abbr,n", MONTHS)
def test_the_abbreviated_month_name_reads(wide, abbr, n):
    """CLDR abbreviates Machi as Mac and Agosti as Ago, not Mar and Aug."""
    assert start_end(f"15 {abbr} 2027") == day(2027, n, 15)


@pytest.mark.parametrize("text,expected", [
    ("5 Juni 2027", (2027, 6, 5)),
    ("25 Desemba 2020", (2020, 12, 25)),
    ("1 Januari 2030", (2030, 1, 1)),
    ("29 Februari 2028", (2028, 2, 29)),
    ("31 Desemba 1999", (1999, 12, 31)),
])
def test_the_date_line_runs_day_month_year(text, expected):
    assert start_end(text) == day(*expected)


def test_a_bare_day_and_month_reads_forward():
    assert start_end("5 Juni") == day(2027, 6, 5)


def test_a_bare_month_is_the_whole_month():
    assert start_end("Julai 2027") == (day(2027, 7, 1)[0], day(2027, 8, 1)[0])


def test_a_month_with_no_year_reads_forward():
    assert start_end("Julai") == (day(2027, 7, 1)[0], day(2027, 8, 1)[0])


@pytest.mark.parametrize("text,expected", [
    ("mnamo 5 Juni", (2027, 6, 5)),
    ("katika 5 Juni 2027", (2027, 6, 5)),
])
def test_the_point_in_time_markers(text, expected):
    assert start_end(text) == day(*expected)


def test_a_bare_four_figure_year():
    assert start_end("2027") == (day(2027, 1, 1)[0], day(2028, 1, 1)[0])


@pytest.mark.parametrize("text", ["27", "127", "5"])
def test_a_short_digit_run_is_not_a_year(text):
    """The year guard wants four figures; a stray count is not a year."""
    r = parse(text)
    assert r is None or r[0].end.year - r[0].start.year != 1 or r[1] != ""


def test_the_day_and_the_month_are_not_swapped():
    """5 Juni is the fifth of June, never the sixth of May.

    CLDR's short pattern for Swahili is dd/MM/y, so the day leads.  Reading it
    the other way round would be silently wrong on every date whose day is a
    valid month number.
    """
    s = span("5 Juni 2027")
    assert (s.start.month, s.start.day) == (6, 5)


def test_a_month_name_alone_is_not_a_number():
    """Mei is May, not a numeral, even though it is short."""
    assert start_end("Mei 2027") == (day(2027, 5, 1)[0], day(2027, 6, 1)[0])


def test_a_nonexistent_date_is_not_invented():
    nomatch("31 Februari 2027")
