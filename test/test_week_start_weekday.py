"""Week-start convention governs "this <weekday>" across locales.

The relative week that "this <weekday>" lands in must follow the locale's
declared ``week_start`` convention, exactly as "this week"/"the weekend" already
do -- not a hardcoded Monday-start week. Gold is computed independently from the
Sunday-/Saturday-start week boundary, never read back from the parser.

Anchor: 2017-06-27, a Tuesday.
  * he (week_start=sunday): the current Sunday-start week is Sun 2017-06-25 ..
    Sat 2017-07-01, so "this Sunday" = 2017-06-25 (the day the week began).
  * ar (week_start=saturday): the current Saturday-start week is Sat 2017-06-24
    .. Fri 2017-06-30, so "this Saturday" = 2017-06-24, "this Sunday" =
    2017-06-25.
  * en (week_start=monday, control): unchanged -- "this Friday" of the Monday
    week Mon 2017-06-26 .. Sun 2017-07-02 is 2017-06-30.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

_ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("text,lang,expected", [
    ("יום ראשון הזה", "he", "2017-06-25"),   # this Sunday, Sunday-start week
    ("السبت هذا", "ar", "2017-06-24"),        # this Saturday, Saturday-start week
    ("الأحد هذا", "ar", "2017-06-25"),        # this Sunday, Saturday-start week
    ("this friday", "en", "2017-06-30"),      # control: Monday-start unchanged
])
def test_this_weekday_honours_week_start(text, lang, expected):
    result = extract_timespan(text, lang, _ANCHOR)
    assert result is not None, f"{lang}: {text!r} did not parse"
    assert result[0].start_datetime.date().isoformat() == expected
