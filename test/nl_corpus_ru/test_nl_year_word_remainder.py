"""Russian: the preposition and the year noun belong to the date.

"в 2024 году" and "2022 год" name the year with the noun "год" after the
number, and "в" opens the time phrase: Wiktionary, s.v. "в", sense 17, "при
указании на конкретное время или период", "В начале июля".  Nothing of the
date stays in the remainder.  The year 2024 runs from 1 January 2024 to
1 January 2025.
"""
from datetime import datetime

import pytest

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text,start,end,remainder", [
    ("в 2024 году", (2024, 1, 1), (2025, 1, 1), ""),
    ("2022 год", (2022, 1, 1), (2023, 1, 1), ""),
    ("октябрь 2024 года", (2024, 10, 1), (2024, 11, 1), ""),
    ("в октябре 2024 года", (2024, 10, 1), (2024, 11, 1), ""),
    ("15 октября 2024 года", (2024, 10, 15), (2024, 10, 16), ""),
    ("в 2024 году я поеду", (2024, 1, 1), (2025, 1, 1), "я поеду"),
    ("на 2024 год", (2024, 1, 1), (2025, 1, 1), ""),
])
def test_year_noun_and_preposition(text, start, end, remainder):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(datetime(*start))
    assert r.span.end == ad(datetime(*end))
    assert r.remainder == remainder


@pytest.mark.parametrize("text,remainder", [
    ("в начале года", ""),
    ("заведи будильник на полседьмого", "заведи будильник"),
    ("перенеси встречу на пятницу", "перенеси встречу"),
])
def test_preposition_folds(text, remainder):
    r = parse(text)
    assert r is not None
    assert r.remainder == remainder


def test_start_of_the_year_starts_on_1_january():
    assert parse("в начале года").span.start == ad(datetime(ANCHOR.year, 1, 1))
