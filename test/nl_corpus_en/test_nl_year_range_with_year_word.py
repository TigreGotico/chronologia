"""A range of spelled years after "the year" or "the years" is one range, also
with a word after it: the range word before the year word cues the second
number too."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, AstroDate


@pytest.mark.parametrize("text, end, rest", [
    ("between the years two thousand and two thousand and ten in Europe",
     2011, "in Europe"),
    ("from the year two thousand to two thousand and ten in Europe",
     2011, "in Europe"),
    ("between the years two thousand and two thousand and ten", 2011, ""),
    ("from the years two thousand to two thousand and five in Europe",
     2006, "in Europe"),
])
def test_a_range_of_years_after_a_year_word_holds_both_years(text, end, rest):
    found = extract_timespan(text, "en", ANCHOR)
    assert (found.span.start, found.span.end, found.remainder) == (
        AstroDate(2000, 1, 1), AstroDate(end, 1, 1), rest)
