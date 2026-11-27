# -*- coding: utf-8 -*-
"""fr: a regional ten never reads as the count 1.

The bare fr tag reads "septante", "nonante" and "huitante" either as the
Belgian and Swiss tens (71 days) or not at all.  "dans septante-et-un jours"
and "dans septante et un jours" read 71 days: 70 + 1, as fr-BE reads
"septante et un".
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration

@pytest.mark.parametrize("text", [
    "dans septante-et-un jours", "dans septante et un jours",
])
def test_a_regional_ten_is_never_read_as_the_count_one(text):
    found = extract_duration(text, "fr", anchor=datetime(2026, 1, 30, 10, 0))
    assert found.duration == timedelta(days=71)
