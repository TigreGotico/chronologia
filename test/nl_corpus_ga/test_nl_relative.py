"""Irish offsets back from the anchor, and the weekday and period references.

The offset marker "ó shin" (ago) TRAILS the quantity it counts back, so the
whole phrase is "<count> <unit> ó shin"; the count may be spelled or written
in digits and both read the same.  The period markers "seo chugainn" (next)
and "seo caite" (last) trail their noun too, and take the definite article
before it.

Expected values are computed with Python date arithmetic against the anchor,
never read back from the parser.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, nomatch, parse, remainder, span, start


@pytest.mark.parametrize("n,form", [
    (1, "lá"), (2, "lá"), (3, "lá"), (5, "lá"), (10, "lá"), (20, "lá"),
])
def test_days_ago_spelled_and_digit_agree(n, form):
    assert start(f"{n} {form} ó shin") == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n,text", [
    (1, "lá ó shin"), (3, "trí lá ó shin"), (5, "cúig lá ó shin"),
    (10, "deich lá ó shin"), (12, "dó dhéag lá ó shin"),
    (20, "fiche lá ó shin"), (21, "fiche a haon lá ó shin"),
    (30, "tríocha lá ó shin"), (100, "céad lá ó shin"),
])
def test_days_ago(n, text):
    assert start(text) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n,text", [
    (1, "seachtain ó shin"), (3, "trí seachtaine ó shin"),
    (10, "deich seachtaine ó shin"),
])
def test_weeks_ago(n, text):
    assert start(text) == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n,text", [
    (1, "mí ó shin"), (3, "trí mhí ó shin"), (6, "sé mhí ó shin"),
])
def test_months_ago(n, text):
    assert start(text) == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("n,text", [
    (1, "bliain ó shin"), (2, "dhá bhliain ó shin"),
    (5, "cúig bliana ó shin"), (10, "deich mbliana ó shin"),
    (100, "céad bliain ó shin"), (1000, "míle bliain ó shin"),
])
def test_years_ago(n, text):
    assert start(text) == ad(ANCHOR - relativedelta(years=n))


@pytest.mark.parametrize("n,text", [
    (1, "uair ó shin"), (2, "dhá uair ó shin"), (5, "cúig huaire ó shin"),
    (10, "deich n-uaire ó shin"),
])
def test_hours_ago(n, text):
    assert start(text) == ad(ANCHOR - timedelta(hours=n))


@pytest.mark.parametrize("n,text", [
    (1, "nóiméad ó shin"), (15, "cúig déag nóiméad ó shin"),
    (30, "tríocha nóiméad ó shin"),
])
def test_minutes_ago(n, text):
    assert start(text) == ad(ANCHOR - timedelta(minutes=n))


@pytest.mark.parametrize("text", ["trí lá ó shin", "dhá bhliain ó shin"])
def test_offset_consumes_everything(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,off", [
    ("inniu", 0), ("inné", -1), ("amárach", 1),
    ("arú inné", -2), ("arú amárach", 2), ("arú amáireach", 2),
])
def test_named_days(text, off):
    d = (ANCHOR + timedelta(days=off)).date()
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (d.year, d.month, d.day)
    assert (s.end - s.start).days == 1


@pytest.mark.parametrize("text,idx", [
    ("Dé Luain", 0), ("Dé Máirt", 1), ("Dé Céadaoin", 2), ("Déardaoin", 3),
    ("Dé hAoine", 4), ("Dé Sathairn", 5), ("Dé Domhnaigh", 6),
])
def test_marked_weekday_names_its_next_occurrence(text, idx):
    ahead = (idx - ANCHOR.weekday()) % 7 or 7
    d = (ANCHOR + timedelta(days=ahead)).date()
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (d.year, d.month, d.day)


@pytest.mark.parametrize("text,idx", [
    ("Luan", 0), ("Máirt", 1), ("Céadaoin", 2), ("Aoine", 4),
    ("Satharn", 5), ("Domhnach", 6),
])
def test_bare_radical_weekday_reads_too(text, idx):
    """The CLDR citation form is already the adverbial "Dé" compound; the
    bare radical noun a modified reference uses names the same day."""
    ahead = (idx - ANCHOR.weekday()) % 7 or 7
    d = (ANCHOR + timedelta(days=ahead)).date()
    assert start(text).day == d.day


@pytest.mark.parametrize("marked,radical", [
    ("Dé Luain", "Luan"), ("Dé hAoine", "Aoine"), ("Dé Sathairn", "Satharn"),
])
def test_marked_and_radical_weekday_agree(marked, radical):
    assert start(marked) == start(radical)


@pytest.mark.parametrize("text,idx", [
    ("an Luan seo chugainn", 0), ("an Aoine seo chugainn", 4),
    ("an Satharn seo chugainn", 5),
])
def test_next_weekday_trails_its_marker(text, idx):
    ahead = (idx - ANCHOR.weekday()) % 7 or 7
    d = (ANCHOR + timedelta(days=ahead)).date()
    assert start(text).day == d.day


@pytest.mark.parametrize("text,idx", [
    ("an Luan seo caite", 0), ("an Aoine seo caite", 4),
])
def test_last_weekday_trails_its_marker(text, idx):
    back = (ANCHOR.weekday() - idx) % 7 or 7
    d = (ANCHOR - timedelta(days=back)).date()
    assert start(text).day == d.day


@pytest.mark.parametrize("nxt,last", [
    ("an Luan seo chugainn", "an Luan seo caite"),
    ("an Aoine seo chugainn", "an Aoine seo caite"),
])
def test_next_and_last_are_opposite_sides_of_the_anchor(nxt, last):
    assert start(nxt) > ad(ANCHOR) > start(last)


def test_next_month_reads_through_the_lenited_noun():
    """"mhí" is listed because the numeral phrase "trí mhí" attests it, so
    the period reference spelled with it resolves too."""
    nxt = ANCHOR + relativedelta(months=1)
    s = span("an mhí seo chugainn")
    assert (s.start.year, s.start.month, s.start.day) == (nxt.year, nxt.month, 1)


@pytest.mark.parametrize("text", [
    "an tseachtain seo chugainn", "an tseachtain seo caite",
])
def test_t_prothesised_week_is_not_read(text):
    """The article prefixes t to a feminine noun beginning with s, and no
    source consulted gives that surface for "seachtain"; it is therefore not
    listed and the phrase is refused rather than guessed."""
    r = parse(text)
    assert r is None or r[1] != ""


def test_weekend_reference():
    s = span("deireadh seachtaine")
    assert s.start.weekday() == 5 and (s.end - s.start).days == 2


def test_next_weekend_reference():
    assert start("an deireadh seachtaine seo chugainn").weekday() == 5


@pytest.mark.parametrize("text", [
    "trí lá", "cúig bliana", "dhá bhliain", "10 lá",
])
def test_offset_without_a_marker(text):
    """A bare count of units is a quantity, not a point in time."""
    nomatch(text)
