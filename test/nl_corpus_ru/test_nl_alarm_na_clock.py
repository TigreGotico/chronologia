"""Russian "будильник на <hour>": the hour an alarm is set for.

"Он ставит будильник мобильного телефона на 7:30" (Wiktionary, s.v.
"будильник") and the Alice commands "Поставь будильник на 8 утра по будням"
and "Переведи будильник на 10 утра" set an alarm with "на" and the hour.  The
part of the day fixes the half; without one, the hour takes its next
twelve-hour reading (ruling 17).  At the 13:04 anchor 07:00 has passed, so
"на семь утра" is 07:00 on 28 June and "на семь" is 19:00 the same day.  A
unit after the number keeps the length reading: "на десять минут".
"""
import pytest

from chronologia import extract_duration

from ._corpus import ANCHOR, ad, parse


def _at(day, hour):
    return ad(ANCHOR.replace(day=day, hour=hour, minute=0, second=0,
                             microsecond=0))


@pytest.mark.parametrize("text,day,hour,remainder", [
    ("поставь будильник на семь утра", 28, 7, "поставь"),
    ("удали будильник на семь", 27, 19, "удали"),
    ("поставь будильник на восемь вечера", 27, 20, "поставь"),
    ("переведи будильник на 10 утра", 28, 10, "переведи"),
    ("будильник на 9", 27, 21, ""),
])
def test_alarm_na_hour(text, day, hour, remainder):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(day, hour)
    assert r.remainder == remainder


@pytest.mark.parametrize("text,minutes", [
    ("поставь будильник на десять минут", 10),
    ("будильник на семь минут", 7),
])
def test_alarm_na_length_stays_a_length(text, minutes):
    assert parse(text) is None
    assert extract_duration(text, "ru")[0].total_seconds() == minutes * 60


def test_alarm_na_day_stays_a_day():
    r = parse("поставь будильник на завтра")
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=0, minute=0))
    assert r.span.end == ad(ANCHOR.replace(day=29, hour=0, minute=0))
