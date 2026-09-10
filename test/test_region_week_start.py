"""A region subtag may move the week boundary; the language default may not.

``week_start`` is a property of the language, and every language keeps the one
its own locale data declares.  Three regions depart from their language: the
United States, Canada and Brazil begin the week on Sunday (CLDR supplemental
``weekData/firstDay``), so a caller who names the region gets the Sunday week
while the bare language code keeps its own.

Anchor: 2017-06-27, a Tuesday.  The Monday-start week containing it runs
2017-06-26 .. 2017-07-03; the Sunday-start week runs 2017-06-25 .. 2017-07-02.
Both boundaries are computed here from the anchor's weekday, never read back
from the parser.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

_ANCHOR = datetime(2017, 6, 27, 13, 4)
#: Monday 2017-06-26 and Sunday 2017-06-25, from the anchor's own weekday.
_MONDAY = _ANCHOR.date() - timedelta(days=_ANCHOR.weekday())
_SUNDAY = _MONDAY - timedelta(days=1)


@pytest.mark.parametrize("text,lang,expected", [
    ("this week", "en", _MONDAY),
    ("this week", "en-GB", _MONDAY),
    ("this week", "en-US", _SUNDAY),
    ("this week", "en-CA", _SUNDAY),
    ("esta semana", "pt", _MONDAY),
    ("esta semana", "pt-PT", _MONDAY),
    ("esta semana", "pt-BR", _SUNDAY),
])
def test_week_begins_on_the_region_day(text, lang, expected):
    result = extract_timespan(text, lang, _ANCHOR)
    assert result is not None, f"{lang}: {text!r} did not parse"
    assert result[0].start_datetime.date() == expected


def test_the_shipped_default_keeps_the_monday_week():
    # the default argument is region-neutral, so a caller who names no
    # language gets the language default and not the US region's Sunday.
    result = extract_timespan("this week", anchor=_ANCHOR)
    assert result is not None
    assert result[0].start_datetime.date() == _MONDAY


def test_a_region_override_does_not_disturb_the_date_order():
    # en-US and the bare code read the numeric date the same way; only the
    # week boundary differs between them.
    for lang in ("en", "en-US"):
        result = extract_timespan("03/04/2018", lang, _ANCHOR)
        assert result is not None, lang
        assert result[0].start_datetime.date().isoformat() == "2018-03-04"
