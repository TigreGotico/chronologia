"""A year spelled in words after a day and a month is the year of the date.

The `nice_date` surfaces of ovos-date-parser write a full date with the year in
words.  Each of these texts is 2024-03-15, and the reader keeps the spelled year
(issue 994).  A locale that dropped it would answer the next 15 March, which is
2018-03-15 at the anchor, Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

ROWS = [
    ("viernes, quince de marzo de dos mil veinticuatro", "es"),
    ("vendredi quinze mars deux-mille-vingt-quatre", "fr"),
    ("sexta-feira, quinze de março de dois mil e vinte e quatro", "pt"),
    ("venerdì, quindici marzo, duemila ventiquattro", "it"),
    ("divendres, quinze de març de dos mil vint-i-quatre", "ca"),
    ("venres, quince de marzo de dous mil vinte e catro", "gl"),
    ("vrijdag vijftien maart tweeduizend vierentwintig", "nl"),
]


@pytest.mark.parametrize("text,lang", ROWS)
def test_the_spelled_year_is_the_year_of_the_date(text, lang):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == datetime(2024, 3, 15)
    assert found.span.end.datetime() == datetime(2024, 3, 16)
    assert found.remainder == ""
