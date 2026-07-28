# -*- coding: utf-8 -*-
"""Exhaustive "Nth <weekday> of <month>" sweep for Catalan.

Sweeps every ordinal (primer/segon/tercer/quart/cinquè/últim) x weekday
(dilluns..diumenge) x month (gener..desembre) at two anchor years.  The
scoped-weekday-of-month construction resolves inside the *anchor* calendar
year (verified independently), so the expected date is derived here by pure
``datetime`` arithmetic that never touches the parser.  A non-existent fifth
occurrence must return no span.

Anchor years 2019 / 2022 are chosen so no (phrase, anchor) pair collides with
the hand-written cases in ``test_scoped_weekday_of_month`` /
``test_nl_scoped_ordinal_higher`` (both anchored 2017).
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import parse, start, ad, nomatch

# Catalan weekday names -> Python weekday index (Monday == 0).
_WEEKDAYS = [
    ("dilluns", 0), ("dimarts", 1), ("dimecres", 2), ("dijous", 3),
    ("divendres", 4), ("dissabte", 5), ("diumenge", 6),
]

# Catalan month names -> month number.  Vowel-initial months elide "de" -> "d'".
_MONTHS = [
    ("gener", 1), ("febrer", 2), ("març", 3), ("abril", 4),
    ("maig", 5), ("juny", 6), ("juliol", 7), ("agost", 8),
    ("setembre", 9), ("octubre", 10), ("novembre", 11), ("desembre", 12),
]

# masculine ordinals; None marks "últim" (last).
_ORDINALS = [
    ("primer", 1), ("segon", 2), ("tercer", 3),
    ("quart", 4), ("cinquè", 5), ("últim", None),
]

_ANCHOR_YEARS = (2019, 2022)


def _month_prep(month_name):
    return "d'" if month_name[0] in "aeiou" else "de "


def _nth_weekday(year, month, weekday, n):
    """First-of-month + offset; None if the nth occurrence spills the month."""
    d = datetime(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    d += timedelta(weeks=n - 1)
    return d if d.month == month else None


def _last_weekday(year, month, weekday):
    if month == 12:
        nxt = datetime(year + 1, 1, 1)
    else:
        nxt = datetime(year, month + 1, 1)
    d = nxt - timedelta(days=1)
    d -= timedelta(days=(d.weekday() - weekday) % 7)
    return d


def _build():
    hit, miss = [], []
    for anchor_year in _ANCHOR_YEARS:
        for wd_name, wd in _WEEKDAYS:
            for mo_name, mo in _MONTHS:
                prep = _month_prep(mo_name)
                for ord_name, n in _ORDINALS:
                    if n is None:
                        art = "l'últim "
                        expected = _last_weekday(anchor_year, mo, wd)
                    else:
                        art = "el %s " % ord_name
                        expected = _nth_weekday(anchor_year, mo, wd, n)
                    text = "%s%s %s%s" % (art, wd_name, prep, mo_name)
                    if expected is None:
                        miss.append((text, anchor_year))
                    else:
                        hit.append((text, anchor_year, expected.date()))
    return hit, miss


_HIT, _MISS = _build()


@pytest.mark.parametrize(
    "text,anchor_year,day",
    _HIT,
    ids=["%s@%d" % (t, y) for t, y, _ in _HIT],
)
def test_nth_weekday_of_month(text, anchor_year, day):
    anchor = datetime(anchor_year, 6, 27, 13, 4)
    assert start(text, anchor) == ad(datetime(day.year, day.month, day.day))
    assert parse(text, anchor)[1] == ""


@pytest.mark.parametrize(
    "text,anchor_year",
    _MISS,
    ids=["%s@%d" % (t, y) for t, y in _MISS],
)
def test_nonexistent_fifth_weekday(text, anchor_year):
    nomatch(text, datetime(anchor_year, 6, 27, 13, 4))
