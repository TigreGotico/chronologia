"""Icelandic relative offsets in both directions, and the three "fyrir" senses.

"fyrir" + dative shifts back ("fyrir þremur dögum" = three days ago) and
"eftir" + accusative shifts forward ("eftir þrjá daga" = in three days).  The
optional "síðan" may close the backward form without changing it.

The same "fyrir" governs the accusative for a different meaning entirely --
"before <event>" ("fyrir næsta sunnudag", "fyrir helgina") -- and that sense
is not an offset.  The pins below assert it never becomes one: the extractor
resolves the event and leaves "fyrir" visible in the remainder rather than
turning a forward reference into a backward one.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, nomatch, parse, remainder, span, start


@pytest.mark.parametrize("n,form", [(1, "einum degi"), (2, "tveimur dögum"),
                                    (3, "þremur dögum"), (4, "fjórum dögum"),
                                    (9, "níu dögum"), (11, "ellefu dögum"),
                                    (20, "tuttugu dögum")])
def test_days_past(n, form):
    assert start(f"fyrir {form}") == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "einn dag"), (3, "þrjá daga"),
                                    (11, "ellefu daga"), (30, "þrjátíu daga")])
def test_days_future(n, form):
    assert start(f"eftir {form}") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "einni viku"), (2, "tveimur vikum"),
                                    (5, "fimm vikum"), (11, "ellefu vikum")])
def test_weeks_past(n, form):
    assert start(f"fyrir {form}") == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(2, "tvær vikur"), (5, "fimm vikur")])
def test_weeks_future(n, form):
    assert start(f"eftir {form}") == ad(ANCHOR + timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(1, "einum mánuði"),
                                    (2, "tveimur mánuðum"),
                                    (11, "ellefu mánuðum")])
def test_months_past(n, form):
    assert start(f"fyrir {form}") == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(2, "tvo mánuði"), (6, "sex mánuði")])
def test_months_future(n, form):
    assert start(f"eftir {form}") == ad(ANCHOR + relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(1, "einu ári"), (2, "tveimur árum"),
                                    (5, "fimm árum"), (10, "tíu árum"),
                                    (100, "hundrað árum")])
def test_years_past(n, form):
    assert start(f"fyrir {form}") == ad(ANCHOR - relativedelta(years=n))


@pytest.mark.parametrize("n,form", [(1, "eitt ár"), (5, "fimm ár"),
                                    (100, "hundrað ár")])
def test_years_future(n, form):
    assert start(f"eftir {form}") == ad(ANCHOR + relativedelta(years=n))


@pytest.mark.parametrize("n,form", [(5, "fimm mínútum"),
                                    (30, "þrjátíu mínútum"),
                                    (45, "fjörutíu og fimm mínútum")])
def test_minutes_past(n, form):
    assert start(f"fyrir {form}") == ad(ANCHOR - timedelta(minutes=n))


@pytest.mark.parametrize("n,form", [(2, "tveimur klukkustundum"),
                                    (10, "tíu klukkustundum")])
def test_hours_past(n, form):
    assert start(f"fyrir {form}") == ad(ANCHOR - timedelta(hours=n))


@pytest.mark.parametrize("phrase,delta", [
    ("fyrir fimm mínútum síðan", timedelta(minutes=-5)),
    ("fyrir þremur dögum síðan", timedelta(days=-3)),
    ("fyrir tveimur vikum síðan", timedelta(weeks=-2)),
])
def test_reinforcing_sidan_is_consumed(phrase, delta):
    """The dative alone already means "ago"; the trailing "síðan" reinforces
    it and must be swallowed rather than stranded."""
    assert start(phrase) == ad(ANCHOR + delta)
    assert remainder(phrase) == ""


@pytest.mark.parametrize("phrase,delta", [
    ("fyrir degi", timedelta(days=-1)),
    ("fyrir viku", timedelta(weeks=-1)),
    ("fyrir klukkustund", timedelta(hours=-1)),
    ("eftir viku", timedelta(weeks=1)),
    ("eftir mánuð", relativedelta(months=1)),
])
def test_bare_singular_offset(phrase, delta):
    """A count of one is left unsaid; the marker plus the singular noun is the
    whole offset."""
    assert start(phrase) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,delta", [
    ("við hittumst eftir þrjá daga", timedelta(days=3)),
    ("minntu mig á eftir tvo mánuði", relativedelta(months=2)),
    ("þetta var fyrir þremur dögum", timedelta(days=-3)),
])
def test_sentence_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("word,off", [("í dag", 0), ("á morgun", 1),
                                      ("í gær", -1), ("í fyrradag", -2)])
def test_named_day(word, off):
    assert start(word) == ad((ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0))


_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("næsta mánudag", _MID + timedelta(days=6)),
    ("næsta föstudag", _MID + timedelta(days=3)),
    ("næsta fimmtudag", _MID + timedelta(days=2)),
    ("síðastliðinn föstudag", _MID - timedelta(days=4)),
    ("síðastliðinn þriðjudag", _MID - timedelta(days=7)),
    ("síðastliðinn miðvikudag", _MID - timedelta(days=6)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


@pytest.mark.parametrize("text", ["næsta föstudag", "síðastliðinn miðvikudag",
                                  "á næsta föstudag"])
def test_weekday_marker_consumed(text):
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,expected_start,expected_days", [
    ("í þessari viku", _MID - timedelta(days=1), 7),
    ("í næstu viku", _MID + timedelta(days=6), 7),
    ("þessa viku", _MID - timedelta(days=1), 7),
])
def test_relative_period(text, expected_start, expected_days):
    s = span(text)
    assert s.start == ad(expected_start)
    assert (s.end - s.start).days == expected_days


def test_offset_needs_marker():
    nomatch("fimm dagar")
    nomatch("þrír dagar")
    nomatch("tvær vikur")


# -- the "fyrir" case trap --------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("fyrir næsta sunnudag", _MID + timedelta(days=5)),
    ("fyrir næsta föstudag", _MID + timedelta(days=3)),
])
def test_fyrir_before_a_weekday_is_not_an_offset_back(text, expected):
    """Accusative "fyrir" means "before <event>", a different construction
    from the dative "ago".  The weekday must still resolve FORWARD, and the
    unread marker must stay visible rather than silently flipping the sign."""
    assert start(text) == ad(expected)
    assert "fyrir" in remainder(text)


def test_fyrir_before_the_weekend_is_not_an_offset_back():
    s = span("fyrir helgina")
    assert s.start > ad(ANCHOR)
    assert "fyrir" in remainder("fyrir helgina")
