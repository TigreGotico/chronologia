"""Month thirds: ``a principios / mediaos / finales de <month>``.

The month is split into three equal spans by wall-clock hours: each boundary
sits at month_start + (days_in_month * 24 / 3) hours (and twice that).  For a
31-day month the cuts fall on the 11th at 08:00 and the 21st at 16:00.
"""
from calendar import monthrange
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad, ANCHOR
from ._gen import MON


def _cases():
    out = []

    def thirds(y, m):
        days = monthrange(y, m)[1]
        start = datetime(y, m, 1)
        b1 = start + timedelta(hours=days * 24 / 3)
        b2 = start + timedelta(hours=days * 24 * 2 / 3)
        end = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
        return [(f"a principios de {MON[m]}", start, b1),
                (f"a mediaos de {MON[m]}", b1, b2),
                (f"a finales de {MON[m]}", b2, end)]

    for m in range(1, 13):
        # ruling 1 (26 November 2026): a part of a month takes its month's
        # year; a month that ended before the anchor is next year's
        y = ANCHOR.year + (m < ANCHOR.month)
        parts = thirds(y, m)
        if m == ANCHOR.month:
            # ruling 1 (26 November 2026): a part of a month is read as a span;
            # a third of the anchor's own month that has ended at the anchor
            # (early and mid June 2017) is that third of June 2018
            nxt = thirds(y + 1, m)
            parts = [p if p[2] > ANCHOR else n for p, n in zip(parts, nxt)]
        out.extend(parts)
    return out


@pytest.mark.parametrize("text,xs,xe", _cases())
def test_month_third(text, xs, xe):
    s, e = start_end(text)
    assert (s, e) == (ad(xs), ad(xe))
