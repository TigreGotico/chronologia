"""Polish relative offsets in both directions.

"za N <unit>" shifts forward (prefix marker), "N <unit> temu" shifts back
(suffix marker).  Unit nouns carry the case the count governs (nominative
plural 2-4, genitive plural 5+: tygodnie/tygodni, miesiące/miesięcy,
lata/lat).  Values mirror the deposited pl period-offset golds against the
Tuesday 2017-06-27 13:04 anchor.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, parse, nomatch


@pytest.mark.parametrize("n,form", [(1, "dzień"), (2, "dni"), (3, "dni"),
                                    (5, "dni"), (10, "dni")])
def test_days_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n", [1, 3, 5, 10])
def test_days_past(n):
    assert start(f"{n} dni temu") == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "tydzień"), (2, "tygodnie"),
                                    (3, "tygodnie"), (5, "tygodni")])
def test_weeks_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(2, "tygodnie"), (5, "tygodni")])
def test_weeks_past(n, form):
    assert start(f"{n} {form} temu") == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(1, "miesiąc"), (2, "miesiące"),
                                    (5, "miesięcy")])
def test_months_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(2, "miesiące"), (5, "miesięcy")])
def test_months_past(n, form):
    assert start(f"{n} {form} temu") == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(1, "rok"), (2, "lata"), (5, "lat"),
                                    (10, "lat")])
def test_years_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + relativedelta(years=n))


@pytest.mark.parametrize("n,form", [(2, "lata"), (5, "lat")])
def test_years_past(n, form):
    assert start(f"{n} {form} temu") == ad(ANCHOR - relativedelta(years=n))


@pytest.mark.parametrize("n", [5, 10, 30, 45])
def test_minutes_future(n):
    assert start(f"za {n} minut") == ad(ANCHOR + timedelta(minutes=n))


@pytest.mark.parametrize("phrase,delta", [
    ("za pięć dni", timedelta(days=5)),
    ("za trzy tygodnie", timedelta(weeks=3)),
    ("za dziesięć minut", timedelta(minutes=10)),
])
def test_spelled_offset(phrase, delta):
    assert start(phrase) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,delta", [
    ("spotkajmy się za 3 dni", timedelta(days=3)),
    ("przypomnij mi za 2 miesiące", relativedelta(months=2)),
    ("to było 3 dni temu", timedelta(days=-3)),
])
def test_sentence_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("word,off", [("dziś", 0), ("jutro", 1),
                                      ("wczoraj", -1), ("pojutrze", 2),
                                      ("przedwczoraj", -2)])
def test_named_day(word, off):
    assert start(word) == ad((ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0))


_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("przyszły poniedziałek", _MID + timedelta(days=6)),
    ("przyszły piątek", _MID + timedelta(days=3)),
    ("zeszły piątek", _MID - timedelta(days=4)),
    ("zeszły wtorek", _MID - timedelta(days=7)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


# deposited NON_MATCHES: marker or number alone is not an offset
def test_offset_needs_marker():
    nomatch("za tygodnie")
    assert parse("2 temu") is None
    nomatch("pięć dni")
