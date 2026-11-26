"""A clock with a "<city> time" phrase is aware, in the city's IANA zone.

The gold instant is zoneinfo arithmetic on the wall time and the zone; the
offset is the one on the target date, so DST applies.  A city word with no
"time" cue does not change the zone.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from chronologia import extract_timespan

SUMMER = datetime(2017, 6, 27, 13, 4)
WINTER = datetime(2017, 1, 10, 13, 4)


def _utc(anchor, day, hour, zone):
    wall = datetime(anchor.year, anchor.month, anchor.day + day, hour, tzinfo=ZoneInfo(zone))
    return wall.astimezone(timezone.utc)


# (lang, text, anchor, days after the anchor day, wall hour, IANA zone)
_ROWS = [
    ("en", "the call is at 3 pm New York time", SUMMER, 0, 15, "America/New_York"),
    ("en", "the call is at 2 pm Los Angeles time", SUMMER, 0, 14, "America/Los_Angeles"),
    ("en", "the review starts at 6 pm London time", SUMMER, 0, 18, "Europe/London"),
    ("en", "we dial in at 7 pm Tokyo time", SUMMER, 0, 19, "Asia/Tokyo"),
    ("en", "the briefing is at 9 pm Sydney time", SUMMER, 0, 21, "Australia/Sydney"),
    ("en", "the call is at 3 pm New York time", WINTER, 0, 15, "America/New_York"),
    ("en", "the briefing is at 9 pm Sydney time", WINTER, 0, 21, "Australia/Sydney"),
    ("en", "the review starts at 6 pm London time", WINTER, 0, 18, "Europe/London"),
    ("en", "the call is at 9 am New York time", SUMMER, 1, 9, "America/New_York"),
    ("pt", "a reunião é às 15h, hora de Nova Iorque", SUMMER, 0, 15, "America/New_York"),
    ("pt", "a reunião começa às 21h, horário de Moscou", SUMMER, 0, 21, "Europe/Moscow"),
    ("pt", "a reunião começa às 18h no horário de Londres", SUMMER, 0, 18, "Europe/London"),
    ("es", "la llamada es a las 16:00, hora de Nueva York", SUMMER, 0, 16, "America/New_York"),
    ("fr", "la réunion commence à 19 h, heure de Sydney", SUMMER, 0, 19, "Australia/Sydney"),
    ("it", "la riunione è fissata alle 16 ora di Mosca", SUMMER, 0, 16, "Europe/Moscow"),
    ("de", "das Treffen beginnt um 18 Uhr Londoner Zeit", SUMMER, 0, 18, "Europe/London"),
    ("de", "das Treffen beginnt um 15 Uhr Los-Angeles-Zeit", SUMMER, 0, 15, "America/Los_Angeles"),
    ("de", "das Treffen beginnt um 20 Uhr Tokyoter Zeit", SUMMER, 0, 20, "Asia/Tokyo"),
    ("de", "das Treffen beginnt um 18 Uhr New-Yorker Zeit", SUMMER, 0, 18, "America/New_York"),
    ("nl", "de vergadering begint om 16 uur New Yorkse tijd", SUMMER, 0, 16, "America/New_York"),
    ("nl", "de vergadering begint om 18 uur Londense tijd", SUMMER, 0, 18, "Europe/London"),
    ("nl", "de vergadering begint om 20 uur Sydney-tijd", SUMMER, 0, 20, "Australia/Sydney"),
    ("da", "mødet starter klokken 14 Los Angeles-tid", SUMMER, 0, 14, "America/Los_Angeles"),
    ("da", "mødet starter klokken 20 Tokyo-tid", SUMMER, 0, 20, "Asia/Tokyo"),
]


@pytest.mark.parametrize("lang,text,anchor,day,hour,zone", _ROWS)
def test_city_time_is_the_city_instant(lang, text, anchor, day, hour, zone):
    start = extract_timespan(text, lang, anchor).span.start
    assert start.tzinfo is not None, text
    assert start.astimezone(timezone.utc) == _utc(anchor, day, hour, zone)


def test_new_york_summer_offset_is_edt():
    start = extract_timespan("at 3 pm New York time", "en", SUMMER).span.start
    assert start.astimezone(timezone.utc).hour == 19


# no zone cue: the city word leaves the clock naive
@pytest.mark.parametrize("lang,text", [
    ("en", "I flew to New York at 3 pm"),
    ("en", "3pm Berlin"),
    ("pt", "voei para Londres às 15h"),
    ("de", "ich fliege um 15 Uhr nach London"),
])
def test_city_without_time_cue_stays_naive(lang, text):
    assert extract_timespan(text, lang, SUMMER).span.start.tzinfo is None


# no clock: a city time phrase alone is no date
@pytest.mark.parametrize("lang,text", [
    ("en", "what is New York time like"),
    ("es", "no sé la hora de Londres"),
])
def test_city_time_without_clock_is_no_date(lang, text):
    assert extract_timespan(text, lang, SUMMER) is None
