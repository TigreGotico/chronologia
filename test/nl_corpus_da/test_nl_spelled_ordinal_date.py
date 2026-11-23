"""Danish spelled-ordinal day-of-month ("femtende april" = the fifteenth of
April).  The ordinal must fold to the exact day, not strand and leave the
whole month.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start


@pytest.mark.parametrize("ordinal,d", [
    ("første", 1),
    ("femte", 5),
    ("ellevte", 11),
    ("femtende", 15),
    ("enogtyvende", 21),
    ("treogtyvende", 23),
    ("tredivte", 30),
])
def test_spelled_ordinal_of_april(ordinal, d):
    assert start(f"{ordinal} april") == ad(datetime(2018, 4, d))


def test_spelled_thirty_first_of_march():
    assert start("enogtredivte marts") == ad(datetime(2018, 3, 31))
