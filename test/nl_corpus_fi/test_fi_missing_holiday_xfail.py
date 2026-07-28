"""BUG: two flagship Finnish civic holidays are missing from the vocabulary.

vappu (May Day, 1 May) and itsenäisyyspäivä (Independence Day, 6 Dec) are
fixed-date national holidays, but the parser does not recognise the holiday
word: given "vappu 2023" it silently discards "vappu" and parses the bare
year, returning the whole of 2023.  Gold below is the true fixed date;
strict-xfail until the vocabulary gains these entries.

Reproduction (anchor 2017-06-27):
    extract_timespan("vappu 2023", "fi", anchor)
    -> 2023-01-01 .. 2024-01-01  (WRONG; should be 2023-05-01, one day)
"""
from datetime import datetime

import pytest

from ._corpus import ad, start

# holiday -> (month, day)
_MISSING = {"vappu": (5, 1), "itsenäisyyspäivä": (12, 6)}

_CASES = [
    (f"{name} {y}", datetime(y, mo, d))
    for y in (2019, 2023, 2027)
    for name, (mo, d) in _MISSING.items()
]


@pytest.mark.xfail(reason="vappu / itsenäisyyspäivä not in holiday vocabulary",
                   strict=True)
@pytest.mark.parametrize("text,dt", _CASES)
def test_missing_fixed_holiday(text, dt):
    assert start(text) == ad(dt)
