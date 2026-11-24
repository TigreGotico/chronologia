# -*- coding: utf-8 -*-
"""ru and uk: a year spoken as an ordinal numeral is the calendar year.

Only the last word of the numeral declines: "две тысячи второй" is 2002
(2000 + the 2nd).  Each phrase runs from 1 January of its year to 1 January
of the next.  Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1336"
ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,year", [
    ("ru", "в две тысячи втором году", 2002),
    ("ru", "в две тысячи двадцать пятом году", 2025),
    ("ru", "в тысяча девятьсот девяносто пятом году", 1995),
    ("ru", "две тысячи двадцать пятый год", 2025),
    ("ru", "в тысяча девятьсот сорок пятом году", 1945),
    ("uk", "у дві тисячі другому році", 2002),
    ("uk", "у дві тисячі двадцять п'ятому році", 2025),
    ("uk", "тисяча дев'ятсот дев'яносто четвертий рік", 1994),
    ("uk", "у тисяча дев'ятсот сорок п'ятому році", 1945),
])
def test_an_ordinal_year_is_the_calendar_year(lang, text, year):
    found = extract_timespan(text, lang, ANCHOR)
    assert (found.span.start.datetime(), found.span.end.datetime()) == (
        datetime(year, 1, 1), datetime(year + 1, 1, 1))
