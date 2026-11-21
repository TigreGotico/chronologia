"""A spelled year before a full stop is a year, whatever word starts the next
sentence.  The full stop ends the clause of the number, so a word after it
counts nothing the number names."""
import pytest

from ._corpus import AstroDate, parse


@pytest.mark.parametrize("text, rest", [
    ("two thousand. Then we moved", "Then we moved"),
    ("two thousand. Dollars were spent", "Dollars were spent"),
    ("two thousand! Everyone cheered", "Everyone cheered"),
    ("two thousand; then we moved", "then we moved"),
])
def test_a_word_after_the_clause_break_does_not_make_the_year_a_count(
        text, rest):
    found = parse(text)
    assert (found.span.start, found.span.end) == (AstroDate(2000, 1, 1),
                                                  AstroDate(2001, 1, 1))
    assert found.remainder == rest
