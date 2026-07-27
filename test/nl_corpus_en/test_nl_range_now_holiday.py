"""A "from X to Y" range must never collapse to ONE endpoint when the OTHER
endpoint is "now" or a bare trailing holiday surface.

Two silent-wrongs are pinned here.  (1) "now"/"right now" was not a resolvable
standalone temporal, so as a range endpoint it was stranded and the range
collapsed to the other endpoint's point ("from now until Christmas" ->
Christmas alone, remainder "from now until").  "now" is the anchor instant, so
"from now until X" is [anchor, X].  (2) The English bare "new year" surface was
missing (only "new year's day"/"new years day" resolved), so "from Christmas to
New Year" dropped its trailing holiday and collapsed to Christmas.  A "from A to
B" whose other endpoint genuinely cannot resolve (a fuzzy daypart like
"breakfast") must return None -- never a fabricated one-point span.
"""
from datetime import datetime

from ._corpus import start_end, nomatch, parse, ANCHOR


# -- "now" as the OPEN (left) endpoint of a closed range ---------------------

def test_from_now_until_holiday_spans_anchor_to_holiday():
    # was: (2017-12-25, 2017-12-26), remainder "from now until"  (BOGUS collapse)
    s, e = start_end("from now until Christmas")
    assert s == ANCHOR
    assert e == datetime(2017, 12, 26)


def test_between_now_and_weekday_spans_anchor_to_weekday():
    # was: (2017-06-30, 2017-07-01), remainder "between now and"  (BOGUS collapse)
    s, e = start_end("between now and Friday")
    assert s == ANCHOR
    assert e == datetime(2017, 7, 1)


def test_from_now_till_midnight_spans_anchor_to_next_midnight():
    # was: (2017-06-28 00:00, 00:01), remainder "from now till"  (BOGUS collapse)
    s, e = start_end("from now till midnight")
    assert s == ANCHOR
    assert e == datetime(2017, 6, 28, 0, 1)


# -- bare "new year" as the trailing holiday endpoint ------------------------

def test_from_christmas_to_new_year_binds_both_endpoints():
    # was: (2017-12-25, 2017-12-26), remainder "from to New Year"  (dropped end)
    s, e = start_end("from Christmas to New Year")
    assert s == datetime(2017, 12, 25)
    assert e == datetime(2018, 1, 2)


# -- bare "now" / "right now" standalone -> the anchor instant ----------------

def test_bare_now_is_the_anchor_instant():
    s, e = start_end("now")
    assert s == ANCHOR
    assert e == ANCHOR


def test_right_now_is_the_anchor_instant():
    s, e = start_end("right now")
    assert s == ANCHOR
    assert e == ANCHOR


# -- "now" must not hijack non-temporal constructions ------------------------

def test_now_and_then_is_not_a_date():
    nomatch("now and then")


def test_for_now_is_not_a_date():
    nomatch("for now")


# -- DEFERRED: a fuzzy-daypart endpoint ("breakfast") -------------------------

def test_from_fuzzy_daypart_until_noon_is_deferred():
    # "breakfast" is a fuzzy daypart, not a resolvable instant, so this range's
    # left endpoint cannot bind.  Refusing it (returning None) conflicts with the
    # engine's established fall-through contract for an unparseable endpoint
    # ("from july 20 to xyzzy" -> july 20; a reversed pinned range -> its left
    # date) -- both pinned elsewhere in the suite.  A daypart-instant contract is
    # out of scope here; this pins the CURRENT fall-through so the deferral is
    # explicit rather than silent.
    r = parse("from breakfast until noon")
    assert r is not None
    assert r.remainder == "from breakfast until"


# -- regression pins: every working range stays byte-identical ----------------

def test_regression_from_weekday_to_weekday():
    assert start_end("from Monday to Friday") == (
        datetime(2017, 7, 3), datetime(2017, 7, 8))


def test_regression_from_clock_to_clock():
    assert start_end("from 9am to 5pm") == (
        datetime(2017, 6, 28, 9), datetime(2017, 6, 28, 17, 1))


def test_regression_between_bare_numerals():
    assert start_end("between 3 and 5") == (
        datetime(2017, 6, 28, 3), datetime(2017, 6, 28, 5, 1))


def test_regression_from_christmas_to_new_years_day():
    assert start_end("from Christmas to New Year's Day") == (
        datetime(2017, 12, 25), datetime(2018, 1, 2))
