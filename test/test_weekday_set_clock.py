# -*- coding: utf-8 -*-
"""A clock after a weekday range or list belongs to every day of the set.

"de lunes a viernes a las ocho" names 08:00 on each day from Monday to Friday,
not a span that starts on Monday.  The answer is the next day of the set at
that clock after the anchor (class 3: the next occurrence, strictly after the
anchor).  A range or list with no clock keeps its reading.

Every expected instant is worked out by hand from the calendar.  The anchor is
Tuesday 2017-06-27 13:04, so Tuesday 08:00 has passed, Wednesday is 06-28,
Friday is 06-30 and the next Monday is 07-03.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
MONDAY_7AM = datetime(2017, 6, 26, 7, 0)
TUESDAY_9AM = datetime(2017, 6, 27, 9, 0)

# text, language, anchor, expected start, expected remainder
SET_CLOCK = [
    ("de lunes a viernes a las ocho de la mañana avísame", "es", ANCHOR,
     datetime(2017, 6, 28, 8, 0), "avísame"),
    ("me lembre de regar as plantas toda segunda e sexta às 8 da manhã", "pt",
     ANCHOR, datetime(2017, 6, 30, 8, 0),
     "me lembre de regar as plantas toda"),
    ("ricordami di chiamare mia madre tutte le sere dal lunedì al venerdì "
     "alle 18", "it", ANCHOR, datetime(2017, 6, 27, 18, 0),
     "ricordami di chiamare mia madre tutte le sere"),
    ("von Montag bis Freitag um 8 Uhr", "de", ANCHOR,
     datetime(2017, 6, 28, 8, 0), ""),
    ("du lundi au vendredi à 8h", "fr", ANCHOR,
     datetime(2017, 6, 28, 8, 0), ""),
    ("с понедельника по пятницу в 8 утра", "ru", ANCHOR,
     datetime(2017, 6, 28, 8, 0), ""),
    ("monday to friday at 8am", "en", ANCHOR, datetime(2017, 6, 28, 8, 0), ""),
    ("wake me monday to friday at 8am please", "en", ANCHOR,
     datetime(2017, 6, 28, 8, 0), "wake me please"),
    ("monday or friday at 8am", "en", ANCHOR, datetime(2017, 6, 30, 8, 0), ""),
    ("monday and friday at 8", "en", ANCHOR, datetime(2017, 6, 30, 8, 0), ""),
    # a range runs forward through the week: friday, saturday, sunday, monday
    ("friday to monday at 8am", "en", ANCHOR, datetime(2017, 6, 30, 8, 0), ""),
    # tuesday 08:00 has passed, so the next day of the set is monday
    ("monday and tuesday at 8am", "en", ANCHOR, datetime(2017, 7, 3, 8, 0), ""),
    # a clock still ahead today is today
    ("segunda a sexta às 8 da manhã", "pt", MONDAY_7AM,
     datetime(2017, 6, 26, 8, 0), ""),
    ("monday to friday at 8am", "en", TUESDAY_9AM,
     datetime(2017, 6, 28, 8, 0), ""),
]


@pytest.mark.parametrize("text,lang,anchor,start,rest", SET_CLOCK)
def test_clock_after_a_weekday_set_names_the_next_day_of_the_set(
        text, lang, anchor, start, rest):
    res = extract_timespan(text, lang, anchor)
    assert res is not None
    assert res.span.start == start
    assert res.span.end == start.replace(minute=start.minute + 1)
    assert res.remainder == rest


def test_a_weekday_range_with_no_clock_keeps_its_span():
    res = extract_timespan("from monday to friday", "en", ANCHOR)
    assert res.span.start == datetime(2017, 7, 3)
    assert res.span.end == datetime(2017, 7, 8)
