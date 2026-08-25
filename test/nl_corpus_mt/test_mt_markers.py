"""Where a Maltese temporal marker stands, and what it governs.

Maltese is a prepositional language: qabel (before), wara (after), minn
(from), sa (until), mindu (since), bejn (between) and kull (every) all PRECEDE
what they govern.  One marker goes the other way.  ``ilu`` is a postposition
meaning "ago" and it trails the count it measures -- "jumejn ilu", two days
ago -- and the future frame it mirrors is equally postposed, with "oħra"
("another") after the unit.

The same surface ``ilu`` also heads a different lexeme entirely: a durative
adverb that PRECEDES its duration and agrees with the subject through a
personal suffix ("Ili jumejn ma norqod", I haven't slept in two days; "Xmun
ilu seba' xhur fil-ħabs", Simon has been in jail for seven months).  That
sense needs an agreement this engine cannot read, so it is refused, and the
refusal is pinned below: a preposed ``ilu`` must never come back as an offset.

The near/far period words are suppletive phrases, not a particle that composes
with any unit: the year is "is-sena d-dieħla" and "is-sena l-oħra", the month
"ix-xahar id-dieħel" and "ix-xahar li għadda", the week "il-ġimgħa d-dieħla"
and "li għaddiet", and a weekday takes a third pattern again.  They ship as
the phrases they are.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, day, nomatch, parse, remainder, span, start_end


# -- ago: postposed ---------------------------------------------------------

@pytest.mark.parametrize("text,delta,width", [
    ("ħames minuti ilu", timedelta(minutes=5), timedelta(minutes=1)),
    ("tliet sigħat ilu", timedelta(hours=3), timedelta(hours=1)),
    ("erba' ġranet ilu", timedelta(days=4), timedelta(days=1)),
    ("sitt ġimgħat ilu", timedelta(weeks=6), timedelta(weeks=1)),
])
def test_ago_trails_the_count_it_measures(text, delta, width):
    back = ANCHOR - delta
    assert start_end(text) == (ad(back), ad(back + width))


@pytest.mark.parametrize("text", [
    "sena ilu", "xahar ilu", "ġimgħa ilu", "siegħa ilu", "minuta ilu",
    "sekonda ilu", "seklu ilu", "jum ilu",
])
def test_a_bare_singular_unit_with_ago_is_one_of_it(text):
    assert remainder(text) == ""


def test_one_year_ago_is_one_year_back():
    back = ANCHOR - relativedelta(years=1)
    assert start_end("sena ilu") == (ad(back), ad(back + relativedelta(years=1)))


# -- the durative homograph: preposed ilu is NOT ago ------------------------

@pytest.mark.parametrize("text", [
    "ilu seba' xhur",
    "ili jumejn",
    "ilha ġimgħa",
    "ilna sentejn",
])
def test_a_preposed_ilu_is_not_an_offset(text):
    # the durative sense needs subject agreement the engine cannot read, so it
    # yields nothing rather than an "ago" answer pointing the wrong way.
    nomatch(text)


def test_the_durative_and_the_ago_reading_are_not_the_same_phrase():
    assert parse("ilu seba' xhur") is None
    assert parse("seba' xhur ilu") is not None


# -- the future frame: preposed frame, postposed "another" ------------------

@pytest.mark.parametrize("text,delta,width", [
    ("fi żmien jumejn oħra", timedelta(days=2), timedelta(days=1)),
    ("fi żmien tliet ġranet oħra", timedelta(days=3), timedelta(days=1)),
    ("fi żmien ħames ġimgħat oħra", timedelta(weeks=5), timedelta(weeks=1)),
    ("fi żmien sitt sigħat oħra", timedelta(hours=6), timedelta(hours=1)),
])
def test_the_future_frame_reads_forward(text, delta, width):
    forward = ANCHOR + delta
    assert start_end(text) == (ad(forward), ad(forward + width))


@pytest.mark.parametrize("text,years", [
    ("fi żmien sentejn oħra", 2),
    ("fi żmien tliet snin oħra", 3),
    ("fi żmien ħdax-il sena oħra", 11),
])
def test_the_future_frame_over_years(text, years):
    forward = ANCHOR + relativedelta(years=years)
    assert start_end(text) == (ad(forward), ad(forward + relativedelta(years=1)))


def test_the_masculine_another_goes_with_the_masculine_unit():
    forward = ANCHOR + relativedelta(months=3)
    assert start_end("fi żmien tliet xhur ieħor") == (
        ad(forward), ad(forward + relativedelta(months=1)))


# -- the suppletive near/far period phrases ---------------------------------

@pytest.mark.parametrize("text,start_iso,end_iso", [
    ("din is-sena", "2027-01-01", "2028-01-01"),
    ("is-sena d-dieħla", "2028-01-01", "2029-01-01"),
    ("is-sena l-oħra", "2026-01-01", "2027-01-01"),
    ("dan ix-xahar", "2027-05-01", "2027-06-01"),
    ("ix-xahar id-dieħel", "2027-06-01", "2027-07-01"),
    ("ix-xahar li għadda", "2027-04-01", "2027-05-01"),
    ("ġimgħa d-dieħla", "2027-05-17", "2027-05-24"),
    ("ġimgħa li għaddiet", "2027-05-03", "2027-05-10"),
])
def test_the_period_phrase_names_its_period(text, start_iso, end_iso):
    s = span(text)
    assert s.start.date().isoformat() == start_iso
    assert s.end.date().isoformat() == end_iso


# -- the preposed prepositions ----------------------------------------------

def test_since_opens_a_range_that_ends_at_the_anchor():
    s = span("mindu 2020")
    assert s.start.date().isoformat() == "2020-01-01"
    assert s.end.date() == ANCHOR.date()


def test_between_two_dates_spans_both():
    s = span("bejn 3 ta' Mejju 2027 u 7 ta' Mejju 2027")
    assert s.start.date().isoformat() == "2027-05-03"
    assert s.end.date().isoformat() == "2027-05-08"


def test_from_one_date_to_another():
    s = span("minn 1 ta' Jannar 2028 sa 5 ta' Frar 2028")
    assert s.start.date().isoformat() == "2028-01-01"
    assert s.end.date().isoformat() == "2028-02-06"


# -- today, yesterday, tomorrow, the day after ------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("illum", 2027, 5, 12),
    ("llum", 2027, 5, 12),
    ("lbieraħ", 2027, 5, 11),
    ("ilbieraħ", 2027, 5, 11),
    ("il-bieraħ", 2027, 5, 11),
    ("għada", 2027, 5, 13),
    ("pitgħada", 2027, 5, 14),
    ("bitgħada", 2027, 5, 14),
])
def test_the_named_days(text, y, m, d):
    assert start_end(text) == day(y, m, d)


# -- the whole this-UNIT family, swept -------------------------------------
# The demonstrative frame has to name the WHOLE unit it modifies, not one day
# inside it.  The week is the one that can go wrong, because Maltese spells
# it with the same noun as Friday; it is swept here alongside every sibling so
# a future change to the article handling cannot quietly shrink one of them.

@pytest.mark.parametrize("text,start_iso,end_iso,days", [
    ("din is-sena", "2027-01-01", "2028-01-01", 365),
    ("dan ix-xahar", "2027-05-01", "2027-06-01", 31),
    ("din il-ġimgħa", "2027-05-10", "2027-05-17", 7),
    ("din il-ġurnata", "2027-05-12", "2027-05-13", 1),
    ("dan il-jum", "2027-05-12", "2027-05-13", 1),
])
def test_the_this_frame_names_the_whole_unit(text, start_iso, end_iso, days):
    s = span(text)
    assert s.start.date().isoformat() == start_iso
    assert s.end.date().isoformat() == end_iso
    assert (s.end_datetime - s.start_datetime).days == days


def test_this_century_is_the_whole_century():
    s = span("dan is-seklu")
    assert (s.start.year, s.end.year) == (2000, 2100)


@pytest.mark.parametrize("text", [
    "din is-siegħa", "din il-minuta", "din is-sekonda",
])
def test_the_sub_day_units_have_no_this_frame(text):
    # a clock-grain "this hour"/"this minute" is not a calendar period this
    # engine resolves, in Maltese as in the other locales; it declines rather
    # than rounding to something it can express.
    nomatch(text)
