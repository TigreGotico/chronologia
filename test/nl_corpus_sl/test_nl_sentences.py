"""Slovenian offsets embedded in full sentences a user would speak."""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, AstroDate, ad, start, span


@pytest.mark.parametrize("text,delta", [
    ("vidiva se čez tri dni", timedelta(days=3)),
    ("pokliči me čez tri ure", timedelta(hours=3)),
    ("opomni me čez deset minut", timedelta(minutes=10)),
    ("to se je zgodilo pred petimi dnevi", None),  # oblique numeral -> gap
    ("bili smo tam pred dvema letoma", None),      # dual instr numeral -> gap
    ("sestanek je čez dva tedna", timedelta(weeks=2)),
    ("pride čez štiri dni", timedelta(days=4)),
    ("javim se čez tri ure", timedelta(hours=3)),
    ("začnemo čez šest mesecev", relativedelta(months=6)),
    ("konča se čez pet dni", timedelta(days=5)),
])
def test_sentence_offset(text, delta):
    if delta is None:
        # oblique/dual spelled numerals are not folded (number-model gap)
        from ._corpus import parse
        assert parse(text) is None
    else:
        assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("n", [4, 6, 7, 8, 9, 12])
def test_more_days(n):
    assert start(f"čez {n} dni") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n", [15, 20, 25, 45])
def test_more_minutes(n):
    assert start(f"čez {n} minut") == ad(ANCHOR + timedelta(minutes=n))


@pytest.mark.parametrize("text,y,m,d", [
    ("rezervacija je 5. junija 2020", 2020, 6, 5),
    ("rojstni dan je 22. marca", 2018, 3, 22),
    ("izpit je 1. septembra 2019", 2019, 9, 1),
])
def test_sentence_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_offset_width():
    assert span("čez 3 dni").width == timedelta(days=1)
    assert span("čez 2 tedna").width == timedelta(weeks=1)
