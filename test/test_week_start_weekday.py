""""this <weekday>" is the first such weekday on or after the anchor.

A named occurrence is the next one strictly after the anchor, and an
occurrence that contains the anchor is the anchor's own.  A weekday already
past in the current week is therefore not "this" one, whatever day the
locale's week starts on: the locale's week start no longer moves "this" back
to a day before the anchor.  Gold is counted on the calendar by hand.

Anchor: 2017-06-27, a Tuesday.  The next Saturday is 2017-07-01, the next
Sunday 2017-07-02, and the next Friday 2017-06-30.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

_ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("text,lang,expected", [
    ("יום ראשון הזה", "he", "2017-07-02"),   # this Sunday; he weeks start Sunday
    ("السبت هذا", "ar", "2017-07-01"),        # this Saturday; ar weeks start Saturday
    ("الأحد هذا", "ar", "2017-07-02"),        # this Sunday
    ("this friday", "en", "2017-06-30"),      # en weeks start Monday
    ("this tuesday", "en", "2017-06-27"),     # the anchor's own weekday
])
def test_this_weekday_is_on_or_after_the_anchor(text, lang, expected):
    result = extract_timespan(text, lang, _ANCHOR)
    assert result is not None, f"{lang}: {text!r} did not parse"
    assert result[0].start_datetime.date().isoformat() == expected
