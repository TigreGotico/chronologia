"""ru and uk: the preposition and the year noun belong to the date.

"в 2024 году" and "у 2024 році" name the year with the noun after the number,
and the preposition opens the time phrase, so nothing of the date stays in the
remainder.  Anchor: Tuesday 2017-06-27 13:04.  The span starts are the ones the
issue lists as right; the expected remainder is empty.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/988"
ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,start,remainder", [
    ("ru", "в начале года", datetime(2017, 1, 1), ""),
    ("uk", "на початку року", datetime(2017, 1, 1), ""),
    ("ru", "в 2024 году", datetime(2024, 1, 1), ""),
    ("uk", "у 2024 році", datetime(2024, 1, 1), ""),
    ("uk", "2024 року", datetime(2024, 1, 1), ""),
    ("ru", "2022 год", datetime(2022, 1, 1), ""),
    ("ru", "октябрь 2024 года", datetime(2024, 10, 1), ""),
])
def test_the_year_noun_and_preposition_are_part_of_the_date(
        lang, text, start, remainder):
    found = extract_timespan(text, lang, ANCHOR)
    assert (found.span.start.datetime(), found.remainder) == (start, remainder)


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_ru_na_before_a_spelled_half_hour_is_part_of_the_date():
    found = extract_timespan("заведи будильник на полседьмого", "ru", ANCHOR)
    assert found.remainder == "заведи будильник"
