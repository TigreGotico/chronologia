"""The relative offset, whose marker always TRAILS the duration it governs.

``առաջ`` counts back and ``անց``/``հետո`` count forward, and all three sit
AFTER the numeral+noun phrase they govern; the forward offset has a fourth
realisation with no free word at all, the ablative suffix on the unit noun
(``երեք օրից``).  Every direction is pinned adversarially -- the opposite
reading is asserted absent, not merely the right one asserted present -- and
so is the position: the same words placed BEFORE the duration must not read
as an offset, because in Armenian they are not adpositions there at all.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, parse, span, start


def _back(**kw):
    return ad(ANCHOR - relativedelta(**kw))


def _forward(**kw):
    return ad(ANCHOR + relativedelta(**kw))


@pytest.mark.parametrize("text,kw", [
    ("երեք օր առաջ", {"days": 3}),
    ("մեկ օր առաջ", {"days": 1}),
    ("երկու շաբաթ առաջ", {"weeks": 2}),
    ("հինգ ամիս առաջ", {"months": 5}),
    ("մեկ տարի առաջ", {"years": 1}),
    ("տասը րոպե առաջ", {"minutes": 10}),
    ("երեք ժամ առաջ", {"hours": 3}),
    ("քառասունհինգ վայրկյան առաջ", {"seconds": 45}),
])
def test_arraj_counts_back(text, kw):
    assert start(text) == _back(**kw)


@pytest.mark.parametrize("text,kw", [
    ("հինգ տարի անց", {"years": 5}),
    ("երեք օր անց", {"days": 3}),
    ("երկու շաբաթ անց", {"weeks": 2}),
    ("երեք օր հետո", {"days": 3}),
    ("տասը րոպե հետո", {"minutes": 10}),
])
def test_ants_and_heto_count_forward(text, kw):
    assert start(text) == _forward(**kw)


@pytest.mark.parametrize("text,kw", [
    ("երեք օրից", {"days": 3}),
    ("երկու շաբաթից", {"weeks": 2}),
    ("հինգ ամսից", {"months": 5}),
    ("երկու տարուց", {"years": 2}),
    ("քսան րոպեից", {"minutes": 20}),
    ("չորս ժամից", {"hours": 4}),
    ("տասը վայրկյանից", {"seconds": 10}),
])
def test_ablative_suffix_counts_forward(text, kw):
    """The forward offset needs no free marker word: the ablative on the unit
    noun carries it, stem changes and all (ամիս -> ամսից, տարի -> տարուց)."""
    assert start(text) == _forward(**kw)


@pytest.mark.parametrize("back,forward", [
    ("երեք օր առաջ", "երեք օր անց"),
    ("երկու շաբաթ առաջ", "երկու շաբաթ հետո"),
    ("հինգ ամիս առաջ", "հինգ ամսից"),
])
def test_the_two_directions_never_collapse(back, forward):
    """առաջ and the forward markers are the two halves of one opposition;
    reading either as the other lands the answer on the wrong side of now."""
    b, f = start(back), start(forward)
    assert b < ad(ANCHOR) < f


@pytest.mark.parametrize("text", [
    "առաջ երեք օր", "անց հինգ տարի", "հետո երեք օր",
])
def test_the_marker_never_leads(text):
    """Placed before the duration these words are an adverb ("forward",
    "then"), not an offset adposition, so the phrase must not read as one."""
    r = parse(text)
    assert r is None or r[1] != ""


def test_bare_singular_unit_reads_as_one():
    """"օր առաջ" -- a day ago, the count unspoken."""
    assert start("օր առաջ") == _back(days=1)


def test_half_quantifier():
    """կես ("half") is the fractional of երկու and quantifies a duration."""
    assert start("կես ժամ առաջ") == ad(ANCHOR - timedelta(minutes=30))


@pytest.mark.parametrize("text,kw", [
    ("հաջորդ շաբաթ", {"weeks": 1}),
    ("նախորդ շաբաթ", {"weeks": -1}),
])
def test_relative_period_marker_leads(text, kw):
    """հաջորդ/նախորդ are prenominal adjectives, the mirror image of the
    postposed offset markers -- position is per-marker in this language."""
    week_start = ANCHOR - timedelta(days=ANCHOR.weekday())
    expected = (week_start + timedelta(weeks=kw["weeks"])).replace(
        hour=0, minute=0, second=0, microsecond=0)
    assert start(text) == ad(expected)


def test_this_year_is_the_calendar_year():
    s, e = span("այս տարի").start, span("այս տարի").end
    assert (s.year, s.month, s.day) == (2017, 1, 1)
    assert (e.year, e.month, e.day) == (2018, 1, 1)


@pytest.mark.parametrize("text,offset", [
    ("այսօր", 0), ("երեկ", -1), ("վաղը", 1), ("վաղն", 1),
    ("նախանցյալ օրը", -2), ("վաղը չէ մյուս օրը", 2),
])
def test_named_days(text, offset):
    expected = (ANCHOR + timedelta(days=offset)).replace(
        hour=0, minute=0, second=0, microsecond=0)
    assert start(text) == ad(expected)


def test_saturday_needs_the_day_noun():
    """շաբաթ alone is the week; only the phrase ``շաբաթ օրը`` names Saturday,
    so "two weeks ago" can never come back as "two Saturdays ago"."""
    assert start("երկու շաբաթ առաջ") == _back(weeks=2)
    assert start("շաբաթ օրը").weekday() == 5


@pytest.mark.parametrize("text,freq", [
    ("ամեն օր", "DAILY"), ("ամեն շաբաթ", "WEEKLY"), ("ամեն ամիս", "MONTHLY"),
    ("ամեն տարի", "YEARLY"),
])
def test_every_opens_a_recurrence(text, freq):
    """ամեն is prenominal and takes no case suffix on the noun it quantifies."""
    from chronologia import extract_recurrence
    r = extract_recurrence(text, "hy", ANCHOR)
    assert r is not None and r[0].freq == freq and r[1] == ""


def test_friday_still_counts_as_a_weekday():
    """The Saturday/week homonymy is local to շաբաթ: a weekday with no unit
    twin still supports the N-weekdays-ago reading."""
    assert start("երկու ուրբաթ առաջ") == ad(
        ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
        - timedelta(days=11))
