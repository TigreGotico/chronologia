"""Croatian offsets and references embedded in full sentences a user would
speak -- the marker/number/date words are consumed, the request survives.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, span


@pytest.mark.parametrize("text,delta", [
    ("vidimo se za tri dana", timedelta(days=3)),
    ("nazovi me za dva sata", timedelta(hours=2)),
    ("podsjeti me za deset minuta", timedelta(minutes=10)),
    ("to se dogodilo prije pet dana", timedelta(days=-5)),
    ("bili smo tamo prije dvije godine", relativedelta(years=-2)),
    ("sastanak je za dva tjedna", timedelta(weeks=2)),
    ("stiže za četiri dana", timedelta(days=4)),
    ("javit ću se za tri sata", timedelta(hours=3)),
    ("dovršeno prije tri tjedna", timedelta(weeks=-3)),
    ("krećemo za šest mjeseci", relativedelta(months=6)),
])
def test_sentence_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("n", [4, 6, 7, 8, 12])
def test_more_days(n):
    assert start(f"za {n} dana") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n", [15, 20, 25, 45])
def test_more_minutes(n):
    assert start(f"za {n} minuta") == ad(ANCHOR + timedelta(minutes=n))


@pytest.mark.parametrize("text,y,m,d", [
    ("rezervacija je 5. lipnja 2020", 2020, 6, 5),
    ("rođendan je 22. ožujka", 2018, 3, 22),
    ("ispit je 1. rujna 2019", 2019, 9, 1),
])
def test_sentence_date(text, y, m, d):
    from ._corpus import AstroDate
    assert start(text) == AstroDate(y, m, d)


def test_offset_width():
    assert span("za 3 dana").width == timedelta(days=1)
    assert span("za 2 tjedna").width == timedelta(weeks=1)
