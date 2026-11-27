"""A spelled year range after "the year" or "the years" is one range.

"between the years two thousand and two thousand and ten in Europe" reads as
its control without the trailing words, "between the years two thousand and
two thousand and ten": the years 2000 to 2010 inclusive, so from 1 January
2000 to 1 January 2011.  The trailing words stay in the remainder.
Anchor: Friday 2026-01-30 10:00.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1054"
ANCHOR = datetime(2026, 1, 30, 10, 0)


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,remainder", [
    ("en", "between the years two thousand and two thousand and ten in Europe",
     "in Europe"),
    ("en", "from the year two thousand to two thousand and ten in Europe",
     "in Europe"),
    ("pt", "desde o ano dois mil até dois mil e dez em Lisboa", "em Lisboa"),
])
def test_a_year_range_keeps_both_years_before_trailing_words(
        lang, text, remainder):
    found = extract_timespan(text, lang, ANCHOR)
    assert (found.span.start.datetime(), found.span.end.datetime(),
            found.remainder) == (
        datetime(2000, 1, 1), datetime(2011, 1, 1), remainder)
