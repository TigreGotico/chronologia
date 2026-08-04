"""A list of distinct dates must yield one mention per item, not just the last.

``extract_timespans`` resolves *every* temporal mention in a sentence.  A
comma/and list of distinct dates was silently collapsing to a single mention --
the spelled-number fold greedily merged a run of adjacent digit tokens (and
digits bridged by "and") into one wrong number ("2019 2020 2021" -> 2021, "2 4
6" -> 6), so the matcher only ever saw the last item.  Two shapes are pinned
here:

* independent complete references ("2019, 2020 and 2021", "March, June and
  September", "Christmas and New Year") -> one mention each;
* ordinals sharing one trailing scope ("the 2nd, 4th and 6th of July", "the 5th
  and the 3rd of the month") -> the shared "of July"/"of the month" distributes
  to each ordinal, one mention per ordinal.

Genuine ranges ("from A to B", "between A and B", ISO "A/B") must stay ONE range
mention; those are pinned as regressions so the list fix never widens into them.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespans

#: a Tuesday, 13:04 -- the shared corpus anchor.
ANCHOR = datetime(2017, 6, 27, 13, 4)


def _starts(text):
    """(year, month, day) of every mention's start, in reading order."""
    ms = extract_timespans(text, "en", ANCHOR)
    return [(m.span.start.year, m.span.start.month, m.span.start.day)
            for m in ms]


# -- (a) independent complete references: one mention each ------------------

def test_year_list_yields_one_mention_per_year():
    # was: 1 mention (2021 only) -- the digit run folded to the last year
    assert _starts("2019, 2020 and 2021") == [
        (2019, 1, 1), (2020, 1, 1), (2021, 1, 1)]


def test_month_list_yields_one_mention_per_month():
    assert _starts("March, June and September") == [
        (2017, 3, 1), (2017, 6, 1), (2017, 9, 1)]


def test_holiday_list_yields_one_mention_per_holiday():
    # each of two named holidays resolves independently in the list
    assert _starts("Christmas and Easter") == [(2017, 12, 25), (2018, 4, 1)]


def test_bare_new_year_resolves_standalone():
    # bare "New Year" now resolves via the dedicated new_year_ref construction,
    # which keeps "new"+"year" as SEPARATE tokens (so it never shadows the
    # hebrew_new_year construction).  Used to be a strict-xfail gap.
    assert _starts("New Year") == [(2018, 1, 1)]


# -- (b) ordinals sharing a trailing scope: scope distributes ---------------

def test_three_ordinals_share_trailing_of_july():
    # was: 1 mention (Jul 6); the shared "of July" now reaches 2nd and 4th too
    assert _starts("the 2nd, 4th and 6th of July") == [
        (2017, 7, 2), (2017, 7, 4), (2017, 7, 6)]


def test_two_ordinals_share_trailing_of_july():
    # was: 1 mention (Jul 4)
    assert _starts("the 2nd and 4th of July") == [
        (2017, 7, 2), (2017, 7, 4)]


def test_ordinals_share_trailing_of_the_month():
    assert _starts("the 5th and the 3rd of the month") == [
        (2017, 7, 5), (2017, 7, 3)]


# -- regression pins: ranges stay ONE mention, never a distributed list -----

def test_ordinal_range_stays_one_mention():
    assert len(extract_timespans(
        "from the 2nd to the 6th of July", "en", ANCHOR)) == 1


def test_year_range_between_stays_one_mention():
    assert len(extract_timespans(
        "between 2019 and 2021", "en", ANCHOR)) == 1


def test_weekday_range_stays_one_mention():
    assert len(extract_timespans(
        "from Monday to Friday", "en", ANCHOR)) == 1


def test_iso_slash_interval_stays_one_mention():
    assert len(extract_timespans("2020-04/2020-06", "en", ANCHOR)) == 1


# -- regression pins: recurrences unchanged (extract_recurrence path) --------

def test_multiweekday_recurrence_is_one_rule_not_a_list():
    from chronologia import extract_recurrence
    rec = extract_recurrence("every Monday, Wednesday and Friday", "en", ANCHOR)
    assert str(rec.recurrence) == "FREQ=WEEKLY;BYDAY=MO,WE,FR"
