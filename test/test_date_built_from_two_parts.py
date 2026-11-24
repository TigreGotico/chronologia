# -*- coding: utf-8 -*-
"""A date built from two parts keeps both: an offset with a clock, a count
from a day word, the nth weekday of a relative period.

Every expected instant is hand arithmetic from the anchor.  Where only the
day is the point of the row, the expected value is the date.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/1034"
LISBON = "Europe/Lisbon"


def _anchor(*args):
    from zoneinfo import ZoneInfo
    return datetime(*args, tzinfo=ZoneInfo(LISBON))


# lang, text, anchor, expected start
START = [
    # "bu 2 həftə əvvəl": two weeks before Tuesday 27 June 2017 is 13 June
    ("az", "bu 2 həftə əvvəl oldu", datetime(2017, 6, 27, 13, 4),
     date(2017, 6, 13)),
    # a count from a day word: 27 June + 5 days = 2 July, + 5 years = 2022
    ("de", "setze den frisörtermin auf 5 tage von heute",
     datetime(2017, 6, 27), date(2017, 7, 2)),
    ("de", "spiele happy birthday musik 5 jahre von heute",
     datetime(2017, 6, 27), date(2022, 6, 27)),
    # next Friday is 30 June, 14 days later is 14 July
    ("de", "wie ist das wetter 2 wochen ab nächsten freitag",
     datetime(2017, 6, 27), date(2017, 7, 14)),
    # Saturday is 1 July, 2 weeks and 6 days later is 21 July
    ("de", "vereinbare den besuch für 2 wochen und 6 tage ab samstag",
     datetime(2017, 6, 27), date(2017, 7, 21)),
    # this Friday is 30 June, 2 days later is 2 July
    ("ca", "Toca satanic black metal 2 dies per a aquest divendres",
     datetime(2017, 6, 27), date(2017, 7, 2)),
    ("ca", "Toca super black metal 2 dies a partir d'aquest divendres",
     datetime(2017, 6, 27), date(2017, 7, 2)),
    # Saturday is 1 July, 2 weeks and 6 days later is 21 July
    ("ca", "concerta cita d'aquí a 2 setmanes i 6 dies després de dissabte",
     datetime(2017, 6, 27), date(2017, 7, 21)),
    # "half of two weeks before christmas": one week before 25 December
    ("en", "half of two weeks before christmas", datetime(2026, 9, 25, 12),
     date(2026, 12, 18)),
    # the last day of the next february, leap year 2028 included
    ("en", "the last day of february", _anchor(2027, 10, 17, 12),
     date(2028, 2, 29)),
    ("en", "the last day of february", _anchor(2026, 10, 17, 12),
     date(2027, 2, 28)),
    # "próximo mes de <month>" names that month
    ("es", "el próximo mes de diciembre", _anchor(2026, 10, 17, 12),
     date(2026, 12, 1)),
    ("es", "el próximo mes de marzo", _anchor(2026, 10, 17, 12),
     date(2027, 3, 1)),
    ("es", "el próximo mes de diciembre", _anchor(2026, 12, 15, 12),
     date(2027, 12, 1)),
    ("es", "el próximo mes de octubre", _anchor(2026, 10, 17, 12),
     date(2027, 10, 1)),
    ("en", "july the fourth", _anchor(2026, 10, 17, 12), date(2027, 7, 4)),
    # the next Tuesday after Tuesday 27 June 2017 13:04 "next week" is 4 July
    ("en", "meeting on tuesday at 4 pm next week", datetime(2017, 6, 27, 13, 4),
     datetime(2017, 7, 4, 16, 0)),
    # a clock after a counted day offset
    ("de", "setze den frisörtermin in 5 tagen um halb 10",
     datetime(2017, 6, 27), datetime(2017, 7, 2, 9, 30)),
    ("de", "in 3 tagen um 15 uhr", datetime(2117, 9, 3, 13, 30),
     datetime(2117, 9, 6, 15, 0)),
    ("he", "תזכיר לי בעוד שלושה ימים בשעה 15:30", datetime(2017, 6, 27, 13, 4),
     datetime(2017, 6, 30, 15, 30)),
    ("he", "תזכיר לי בעוד שלושה ימים בשעה 15:30", datetime(2018, 6, 5, 9, 0),
     datetime(2018, 6, 8, 15, 30)),
    # a date with a clock: the lone hour keeps its first reading on a day
    # that is not today
    ("it", "il 3 novembre alle 5", _anchor(2026, 10, 17, 12),
     datetime(2026, 11, 3, 5, 0)),
    ("it", "appuntamento il 15 giugno alle tre", datetime(2017, 6, 27, 13, 4),
     datetime(2018, 6, 15, 3, 0)),
    # the Monday of next week, said on Saturday 17 October 2026
    ("pt-PT", "na segunda semana que vem", _anchor(2026, 10, 17, 12),
     date(2026, 10, 19)),
    ("pt-BR", "na segunda semana que vem", _anchor(2026, 10, 17, 12),
     date(2026, 10, 19)),
    # "within" an offset is the anchor plus the offset
    ("nl", "binnen 3 uur", datetime(2017, 6, 27, 13, 4),
     datetime(2017, 6, 27, 16, 4)),
    ("de", "wir bekommen das ergebnis innerhalb eines tages",
     datetime(2017, 6, 27), datetime(2017, 6, 28)),
    ("eu", "arratsaldea 5:00", datetime(2017, 6, 27, 13, 4),
     datetime(2017, 6, 27, 17, 0)),
    ("it", "novembre dell'anno prossimo", datetime(2026, 10, 17, 12),
     date(2027, 11, 1)),
    ("es", "el 5 de noviembre del año que viene", datetime(2026, 10, 17, 12),
     date(2027, 11, 5)),
]


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,anchor,expected", START)
def test_the_reading_keeps_both_parts(lang, text, anchor, expected):
    start = extract_timespan(text, lang, anchor).span.start.datetime()
    assert (start.date() if isinstance(expected, date)
            and not isinstance(expected, datetime) else start) == expected


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,anchor,expected", [
    ("nl", "binnen 3 uur", datetime(2026, 10, 17, 12, 0),
     datetime(2026, 10, 17, 15, 0)),
    ("es", "el mes de diciembre", _anchor(2026, 10, 17, 12),
     datetime(2026, 12, 1)),
    ("es", "el mes de enero", _anchor(2026, 10, 17, 12),
     datetime(2027, 1, 1)),
])
def test_the_whole_phrase_is_the_date(lang, text, anchor, expected):
    found = extract_timespan(text, lang, anchor)
    assert found.span.start.datetime() == expected
    assert found.remainder == ""


@pytest.mark.xfail(strict=True, reason=ISSUE)
def test_half_of_two_weeks_before_easter_monday_keeps_the_clock():
    # Easter Monday 2027 is 29 March; one week before is 22 March
    found = extract_timespan(
        "half of two weeks before easter monday at 9am", "en",
        datetime(2026, 9, 25, 12))
    assert found.span.start.datetime() == datetime(2027, 3, 22, 9, 0)
    assert found.remainder == ""


@pytest.mark.xfail(strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text", [
    ("es", "cada mañana"), ("gl", "cada mañá"), ("ast", "cada mañana"),
])
def test_cada_before_a_part_of_the_day_leaves_nothing_over(lang, text):
    found = extract_timespan(text, lang, _anchor(2026, 10, 17, 12))
    assert found.remainder == ""
    assert (found.span.end.datetime() - found.span.start.datetime()).days == 0
