"""Arabic writes the day before yesterday with the ordinal on either side.

"أول أمس" fronts the ordinal and "أمس الأول" follows the day word with it;
both name the day before yesterday.  The second form is the one that failed:
the ordinal folded to 1 before the multiword pass could merge the phrase, so
the day word answered alone and the phrase resolved to YESTERDAY -- a wrong
date rather than a refusal.

Anchor 2017-06-27, a Tuesday, so the day before yesterday is Sunday the 25th.
"""
import pytest

from ._corpus import AstroDate, parse, start


@pytest.mark.parametrize("text", [
    "أمس الأول",
    "امس الاول",
    "أول أمس",
    "أول من أمس",
])
def test_day_before_yesterday(text):
    assert start(text) == AstroDate(2017, 6, 25)
    assert parse(text).remainder == ""


def test_the_day_word_alone_is_still_yesterday():
    assert start("أمس") == AstroDate(2017, 6, 26)


@pytest.mark.parametrize("text,month", [
    # the ordinal must still fold inside a month name -- the reason the
    # licence has a suppression guard at all
    ("تشرين الأول", 10),
    ("كانون الثاني", 1),
])
def test_the_month_names_keep_their_ordinal(text, month):
    got = start(text)
    assert (got.month, got.day) == (month, 1)
