"""Ukrainian "будильник на <hour>": the hour an alarm is set for.

"будильник: годинник із спеціальним механізмом, що дзвонить у потрібний час"
(Wiktionary, s.v. "будильник"), and "на" with the accusative "Уживається при
позначенні часу, коли відбувається якась дія" (СУМ-11, s.v. на 1, sense 9).
The part of the day fixes the half; without one, the hour takes its next
twelve-hour reading (ruling 17).  At the 13:04 anchor 07:00 has passed, so
"на сьому ранку" is 07:00 on 28 June and "на сьому" is 19:00 the same day.
"""
import pytest

from chronologia import extract_duration

from ._corpus import ANCHOR, ad, parse


def _at(day, hour):
    return ad(ANCHOR.replace(day=day, hour=hour, minute=0, second=0,
                             microsecond=0))


@pytest.mark.parametrize("text,day,hour,remainder", [
    ("поставити будильник на сьому ранку", 28, 7, "поставити"),
    ("будильник на сьому", 27, 19, ""),
    ("будильник на 7", 27, 19, ""),
    ("постав будильник на восьму вечора", 27, 20, "постав"),
])
def test_alarm_na_hour(text, day, hour, remainder):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(day, hour)
    assert r.remainder == remainder


def test_alarm_na_length_stays_a_length():
    assert parse("будильник на десять хвилин") is None
    assert extract_duration("будильник на десять хвилин", "uk")[0].total_seconds() == 600
