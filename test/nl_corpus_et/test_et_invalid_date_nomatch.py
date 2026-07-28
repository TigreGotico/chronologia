"""Estonian impossible calendar dates must decline, not fabricate a span.

A day number that cannot exist in the named month (31 April, 31 June, 30/29
February in a common year, 29 February on a non-leap century year) has no
referent; the engine returns ``None`` rather than rolling or clamping.
"""
import pytest

from ._corpus import nomatch


@pytest.mark.parametrize("text", [
    "31. aprill 2019",
    "31. aprilli 2019",
    "31. juuni 2019",
    "31. september 2019",
    "31. novembri 2019",
    "30. veebruar 2019",
    "29. veebruar 2019",
    "29. veebruari 2015",
    "29. veebruar 2100",   # 2100 is not a leap year
    "32. jaanuar 2019",
])
def test_impossible_date_nomatch(text):
    nomatch(text)
