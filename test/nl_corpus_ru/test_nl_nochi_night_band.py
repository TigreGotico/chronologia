"""Russian "ночи" is a night band that crosses midnight.

"ночь" is "Часть суток от захода до восхода солнца, от вечера до утра"
(gramota.ru, metaslovar, s.v. ночь, sense 1), so "11 часов ночи" is 23:00 and
"3 часа ночи" is 03:00.  At the 13:04 anchor, 22:00 and 23:00 are still ahead
today; 03:00 and midnight fall on 28 June.
"""
import pytest

from ._corpus import ANCHOR, ad, parse


def _at(day, hour):
    return ad(ANCHOR.replace(day=day, hour=hour, minute=0, second=0,
                             microsecond=0))


@pytest.mark.parametrize("text,day,hour", [
    ("11 часов ночи", 27, 23),
    ("в 10 часов ночи", 27, 22),
    ("3 часа ночи", 28, 3),
    ("в 12 часов ночи", 28, 0),
    ("в 3 часа утра", 28, 3),
])
def test_night_hours(text, day, hour):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(day, hour)
    assert r.remainder == ""
