"""R168 (bg): a digit clock followed by the spoken hour noun ("в 9 часа")
must consume that noun into the CLOCK construction, not strand it in the
remainder -- including when a day-part meridiem ("следобед") follows and
composes the hour to its afternoon reading (9 -> 21:00).  Bulgarian counts
the hour with the count-form noun "часа" for a plural numeral and the bare
"час" for one.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text", ["в 9 часа", "в 1 час"])
def test_digit_clock_consumes_hour_word(text):
    r = parse(text)
    assert r is not None
    hour = 9 if "9" in text else 1
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=hour, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""


def test_digit_clock_consumes_hour_word_then_daypart():
    r = parse("в 9 часа следобед")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(hour=21, minute=0, second=0,
                                             microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""
