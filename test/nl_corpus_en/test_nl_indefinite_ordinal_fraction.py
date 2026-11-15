"""An ordinal after "a" or "an" is a fraction, not a day of the month.

"a third of the month is gone" says a share of the month has passed.  It
names no date.  With the definite article or none, the same words name a day:
"the third of the month" is the 3rd.  The anchor is Tuesday 2017-06-27, so the
coming 3rd is 2017-07-03.
"""
from datetime import datetime

import pytest

from ._corpus import ad, nomatch, start


@pytest.mark.parametrize("text", [
    "a third of the month is gone",
    "we lost a fourth of this month to rain",
    "an eighth of next month is left",
    "a fifth of the month went on rent",
])
def test_fraction_of_the_month_gives_none(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "the third of the month",
    "third of the month",
    "on the third of the month",
])
def test_definite_ordinal_day_of_month_survives(text):
    assert start(text) == ad(datetime(2017, 7, 3))
