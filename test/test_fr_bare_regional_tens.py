# -*- coding: utf-8 -*-
"""fr: a regional ten never reads as the count 1.

The bare fr tag reads "septante", "nonante" and "huitante" either as the
Belgian and Swiss tens (71 days) or not at all.  "dans septante-et-un jours"
and "dans septante et un jours" read 1 day with "dans septante-et" left over,
a wrong value.  71 days is 70 + 1 (fr-BE reads "septante et un" as 71).
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1075"


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
@pytest.mark.parametrize("text", [
    "dans septante-et-un jours", "dans septante et un jours",
])
def test_a_regional_ten_is_never_read_as_the_count_one(text):
    found = extract_duration(text, "fr", anchor=datetime(2026, 1, 30, 10, 0))
    assert found is None or found.duration == timedelta(days=71)
