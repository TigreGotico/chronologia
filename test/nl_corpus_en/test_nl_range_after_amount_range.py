"""A range that opens a later clause is read when the range before it holds
amounts: the first range takes no date, and the second one is the date."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, AstroDate


@pytest.mark.parametrize("text, rest", [
    ("from two thousand to three thousand dollars, "
     "from two thousand to two thousand and ten",
     "from two thousand to three thousand dollars"),
    ("between two thousand and three thousand dollars, "
     "between the years two thousand and two thousand and ten",
     "between two thousand and three thousand dollars"),
])
def test_a_range_of_years_after_a_range_of_amounts_is_the_date(text, rest):
    found = extract_timespan(text, "en", ANCHOR)
    assert (found.span.start, found.span.end, found.remainder) == (
        AstroDate(2000, 1, 1), AstroDate(2011, 1, 1), rest)


def test_a_range_of_amounts_alone_reads_no_date():
    assert extract_timespan("from two thousand to three thousand dollars",
                            "en", ANCHOR) is None
