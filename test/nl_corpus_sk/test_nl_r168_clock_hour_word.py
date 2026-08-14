"""R168 (sk): a digit clock followed by the spoken hour noun ("o 9 hodine")
must consume that noun into the CLOCK construction, not strand it in the
remainder.  Slovak names the hour after "o" in the locative singular
("hodine") or, with the noun read as a bare count, the genitive plural
("hodín").
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text", ["o 9 hodine", "o 9 hodín"])
def test_digit_clock_consumes_hour_word(text):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=9, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""
