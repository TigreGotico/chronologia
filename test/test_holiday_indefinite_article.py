"""A holiday name made of an adjective and a weekday is refused after an
indefinite article ("have a good friday"), and kept everywhere else.

The anchor is Friday 2026-09-25 12:00. Easter Sunday 2027 is 28 March
(Gregorian computus, Meeus), so Good Friday 2027 is 26 March 2027 and Easter
Monday 2027 is 29 March 2027.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2026, 9, 25, 12, 0)
GOOD_FRIDAY = AstroDate(2027, 3, 26)
EASTER_MONDAY = AstroDate(2027, 3, 29)


@pytest.mark.parametrize("lang,text", [
    ("en", "have a good friday"),
    ("en", "I hope you have a good friday"),
    ("en", "an easter monday"),
    ("nl", "een goede vrijdag"),
    ("nl", "ik wens je een goede vrijdag"),
])
def test_indefinite_article_refuses_the_holiday(lang, text):
    assert extract_timespan(text, lang, ANCHOR) is None


@pytest.mark.parametrize("lang,text,start", [
    ("en", "good friday", GOOD_FRIDAY),
    ("en", "see you on good friday", GOOD_FRIDAY),
    ("en", "the good friday service", GOOD_FRIDAY),
    ("en", "easter monday", EASTER_MONDAY),
    ("nl", "goede vrijdag", GOOD_FRIDAY),
    ("nl", "op goede vrijdag", GOOD_FRIDAY),
    ("de", "einen schönen Karfreitag", GOOD_FRIDAY),
    ("de", "am Karfreitag", GOOD_FRIDAY),
    ("pt", "a sexta-feira santa", GOOD_FRIDAY),
    ("pt", "na sexta-feira santa", GOOD_FRIDAY),
    ("es", "el viernes santo", GOOD_FRIDAY),
])
def test_other_readings_keep_the_holiday(lang, text, start):
    got = extract_timespan(text, lang, ANCHOR)
    assert got is not None, f"{text!r} lost the holiday"
    assert got.span.start == start


def test_single_word_name_after_indefinite_article_is_kept():
    assert extract_timespan("a christmas", "en", ANCHOR).span.start == \
        AstroDate(2026, 12, 25)
