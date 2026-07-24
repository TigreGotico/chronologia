"""Wave 2 -- the weekend: this/next/last weekend, a named two-day span.

The Saturday-Sunday of the anchor's week, shifted a whole week per the
relative marker.  Expected spans come from independent calendar
arithmetic against this corpus's anchor -- never by pinning the parser.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, parse, span


def _expected(rel):
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    sat = (base - timedelta(days=base.weekday())
           + timedelta(days=5) + timedelta(weeks=rel))
    end = sat + timedelta(days=2)
    return (AstroDate(sat.year, sat.month, sat.day),
            AstroDate(end.year, end.month, end.day))


CASES = [
    ('this weekend', 0),
    ('next weekend', 1),
    ('last weekend', -1),
    ('the weekend', 0),
    ('weekend', 0),
]


@pytest.mark.parametrize("text,rel", CASES)
def test_weekend(text, rel):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel)


# -- the hyphenated spelling ----------------------------------------------
#
# "week-end" is the older spelling of the same two days and is shipped in the
# English weekend vocabulary, but the hyphen splits it into two tokens; the
# unit noun "week" then claimed the first half and "this week-end" quietly
# read as the whole week.  It names the weekend like the closed spelling.

HYPHEN_CASES = [
    ('this week-end', 0),
    ('next week-end', 1),
    ('last week-end', -1),
    ('the week-end', 0),
    ('week-end', 0),
]


@pytest.mark.parametrize("text,rel", HYPHEN_CASES)
def test_hyphenated_weekend(text, rel):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel)


def test_hyphenated_weekend_is_fully_consumed():
    assert parse('this week-end').remainder == ''


def test_the_week_is_still_the_week():
    # the fix must not make "week" itself weekend-shaped: "this week" is the
    # seven-day span it always was
    sp = span('this week')
    assert (sp.end - sp.start) == timedelta(days=7)
