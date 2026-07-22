# -*- coding: utf-8 -*-
"""Ordinal counting from the anchor (uk). "weekend after next" = skip one
weekend, take the following one. Anchor 2017-06-27 (Tue, weekend_start Sat);
this week's weekend is 2017-07-01/02, so after-next is 2017-07-15 (+2 weeks).
The "N weekday from now" form is unnatural in uk (no colloquial "from now"
marker), so it is xfailed."""
from datetime import timedelta
import pytest
from ._corpus import AstroDate, span, start, nomatch


def test_weekend_after_next():
    s = span("вихідні після наступних")
    assert (s.start.year, s.start.month, s.start.day) == (2017, 7, 15)
    assert s.width == timedelta(days=2)


@pytest.mark.xfail(reason="no colloquial 'from now' present-marker in uk; the "
                          "N-weekday-from-now count does not fire",
                   strict=True)
def test_weekday_from_now():
    # would be the 3rd понеділок strictly after the anchor
    assert start("3 понеділок після наступних") == AstroDate(2017, 7, 17)
