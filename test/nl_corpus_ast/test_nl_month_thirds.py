"""Month thirds: ``a principios / mediaos / finales de <month>``.

The month is split into three equal spans by wall-clock hours: each boundary
sits at month_start + (days_in_month * 24 / 3) hours (and twice that).  For a
31-day month the cuts fall on the 11th at 08:00 and the 21st at 16:00.
"""
from calendar import monthrange
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad
from ._gen import MON


def _cases():
    out = []
    for m in range(1, 13):
        days = monthrange(2017, m)[1]
        start = datetime(2017, m, 1)
        b1 = start + timedelta(hours=days * 24 / 3)
        b2 = start + timedelta(hours=days * 24 * 2 / 3)
        end = datetime(2018, 1, 1) if m == 12 else datetime(2017, m + 1, 1)
        out.append((f"a principios de {MON[m]}", start, b1))
        out.append((f"a mediaos de {MON[m]}", b1, b2))
        out.append((f"a finales de {MON[m]}", b2, end))
    return out


@pytest.mark.parametrize("text,xs,xe", _cases())
def test_month_third(text, xs, xe):
    s, e = start_end(text)
    assert (s, e) == (ad(xs), ad(xe))
