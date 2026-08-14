"""R168 (uk): a digit clock followed by the spoken hour noun ("о 9 годині")
must consume that noun into the CLOCK construction, not strand it in the
remainder.  Ukrainian names the hour after "о" in the locative singular
("годині") or, with the noun read as a bare count, the genitive plural
("годин").
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text", ["о 9 годині", "о 9 годин"])
def test_digit_clock_consumes_hour_word(text):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=9, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""


def test_digit_clock_consumes_hour_word_then_daypart():
    r = parse("о 9 годині ранку")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=9, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""
