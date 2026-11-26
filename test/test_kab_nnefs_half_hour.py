# -*- coding: utf-8 -*-
"""kab "sebɛa u nnefṣ" is half past seven.

Anchor: Tuesday 2017-06-27 13:04.  A lone hour 1 to 12 takes the next
twelve-hour reading (ruling 17), so seven is 19:00 the same day and half past
seven is 19:30.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1021"


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=ISSUE)
def test_sebea_u_nnefs_is_half_past_seven():
    found = extract_timespan(
        "sbedd-iyi-d alarme ɣef sebɛa u nnefṣ", "kab",
        datetime(2017, 6, 27, 13, 4))
    assert found is not None, "no reading for 'sbedd-iyi-d alarme ɣef sebɛa u nnefṣ'"
    assert found.span.start.datetime() == datetime(2017, 6, 27, 19, 30)
    assert found.remainder == "sbedd-iyi-d alarme"
