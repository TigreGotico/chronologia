"""ISO-8601 time-interval form with a slash separator: "2020/2021",
"2020-04/2020-06".

ISO-8601 §4.4.1 writes an interval as two dates joined by a solidus "/".  The
span runs from the start of the first endpoint to the start-of-next of the last
-- exactly what the dash-set year range ("2020-2021") and the spelled
"from ... to ..." already mean.  The slash is trusted as an interval separator
ONLY when BOTH sides independently parse as year-first ISO dates, so the
English numeric date ("06/15/2020", month-first) and a lone slashed pair
("04/2020", "2020/04") are left untouched.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch, parse


@pytest.mark.parametrize("text,s,e", [
    ("2020/2021", (2020, 1, 1), (2022, 1, 1)),
    ("1914/1918", (1914, 1, 1), (1919, 1, 1)),
    ("2020-04/2020-06", (2020, 4, 1), (2020, 7, 1)),
    ("2020-01/2020-12", (2020, 1, 1), (2021, 1, 1)),
])
def test_iso_slash_interval(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


def test_slash_reads_as_the_dash_range_and_spelled_range_do():
    """The slash is only the ISO separator for "from ... to ...", so the
    three surfaces resolve to the identical span."""
    assert start_end("2020/2021") == start_end("2020-2021")
    assert start_end("2020/2021") == start_end("from 2020 to 2021")
    assert start_end("2020-04/2020-06") == start_end("2020-04 to 2020-06")


def test_slash_interval_inside_a_sentence():
    s, e = start_end("the project ran 2020/2021")
    assert (s, e) == (AstroDate(2020, 1, 1), AstroDate(2022, 1, 1))


# -- the numeric-date behaviour the interval rule must NOT disturb ----------

def test_english_numeric_date_is_still_month_first():
    assert start_end("06/15/2020") == (AstroDate(2020, 6, 15),
                                       AstroDate(2020, 6, 16))
    assert start_end("12/11/2024") == (AstroDate(2024, 12, 11),
                                       AstroDate(2024, 12, 12))


@pytest.mark.parametrize("text", ["2024/03", "04/2020", "2020/04"])
def test_a_non_year_first_slashed_pair_is_not_an_interval(text):
    """A slashed pair where a side is not a year-first ISO date is not an
    interval (and, in English, not a numeric date either) -- it stays a
    broken date that names nothing, exactly as before."""
    nomatch(text)


@pytest.mark.parametrize("text", ["/", "//", "2020/", "/2021"])
def test_degenerate_slashes_never_raise(text):
    parse(text)
