"""Ukrainian: the preposition and the year noun belong to the date.

"у 2024 році" and "2024 року" name the year with the noun "рік" after the
number (Wiktionary, s.v. "рік": Р. "року", М. "році"), and "у" or "на" opens
the time phrase (СУМ-11, s.v. в 2, sense 20; s.v. на 1, sense 9).  Nothing of
the date stays in the remainder.  The year 2024 runs from 1 January 2024 to
1 January 2025.
"""
from datetime import datetime

import pytest

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text,start,end,remainder", [
    ("у 2024 році", (2024, 1, 1), (2025, 1, 1), ""),
    ("в 2024 році", (2024, 1, 1), (2025, 1, 1), ""),
    ("2024 року", (2024, 1, 1), (2025, 1, 1), ""),
    ("у жовтні 2024 року", (2024, 10, 1), (2024, 11, 1), ""),
    ("15 жовтня 2024 року", (2024, 10, 15), (2024, 10, 16), ""),
])
def test_year_noun_and_preposition(text, start, end, remainder):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(datetime(*start))
    assert r.span.end == ad(datetime(*end))
    assert r.remainder == remainder


def test_start_of_the_year_keeps_na():
    r = parse("на початку року")
    assert r.span.start == ad(datetime(ANCHOR.year, 1, 1))
    assert r.remainder == ""
