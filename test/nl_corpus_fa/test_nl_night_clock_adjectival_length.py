# -*- coding: utf-8 -*-
"""A spelled hour with a part of the day, and the adjectival length "ده دقیقه‌ای".

"شب" is the night band that crosses midnight, as ru "ночи" is: Wiktionary "شب"
gives the senses "night" and "evening", so "هشت شب" is 20:00 and "سه شب" is
03:00.  A spelled hour followed by a part of the day names a clock with no
"ساعت" before it ("برای هفت صبح": for seven in the morning).

"ـای" is the adjectival suffix of a word that ends in "ـه" (Wiktionary "ـای"),
so "ده دقیقه‌ای" is "ten-minute" and reads as "ده دقیقه" does.

Anchor Tuesday 2017-06-27 13:04.  Expected instants are worked out from the
anchor by hand: an hour already gone by today lands on 06-28, one still ahead
lands on 06-27 (ruling C), and the night hours 6 to 11 are the evening and
1 to 5 the small hours after midnight.
"""
from datetime import timedelta

import pytest

from chronologia import extract_duration

from ._corpus import ANCHOR, parse


@pytest.mark.parametrize("text,want,rest", [
    ("یک زنگ ساعت برای هفت صبح بگذار", (2017, 6, 28, 7, 0),
     "یک زنگ ساعت برای بگذار"),
    ("یک هشدار جدید برای ساعت هشت شب تنظیم کن", (2017, 6, 27, 20, 0),
     "یک هشدار جدید برای تنظیم کن"),
    ("ساعت هشت شب", (2017, 6, 27, 20, 0), ""),
    ("ساعت ده شب", (2017, 6, 27, 22, 0), ""),
    ("ساعت یازده شب", (2017, 6, 27, 23, 0), ""),
    ("ساعت دوازده شب", (2017, 6, 28, 0, 0), ""),
    ("ساعت سه شب", (2017, 6, 28, 3, 0), ""),
    ("ساعت هشت و نیم شب", (2017, 6, 27, 20, 30), ""),
    ("ساعت ۸ شب", (2017, 6, 27, 20, 0), ""),
    ("ساعت پنج عصر", (2017, 6, 27, 17, 0), ""),
    ("ساعت هشت صبح", (2017, 6, 28, 8, 0), ""),
    ("هفت صبح", (2017, 6, 28, 7, 0), ""),
])
def test_spelled_hour_with_a_part_of_the_day(text, want, rest):
    r = parse(text)
    assert r is not None, "%r did not parse" % text
    s = r[0].start
    assert (s.year, s.month, s.day, s.hour, s.minute) == want
    assert r[0].end.minute == want[4] + 1
    assert r[1] == rest


@pytest.mark.parametrize("text,want,rest", [
    ("یک تایمر ده دقیقه‌ای بگذار", timedelta(minutes=10),
     "یک تایمر بگذار"),
    ("یک تایمر بیست ثانیه‌ای بگذار", timedelta(seconds=20),
     "یک تایمر بگذار"),
    ("یک تایمر ۱۵ دقیقه‌ای بگذار", timedelta(minutes=15),
     "یک تایمر بگذار"),
    ("یک تایمر ده دقیقه بگذار", timedelta(minutes=10), "یک تایمر بگذار"),
])
def test_adjectival_length(text, want, rest):
    r = extract_duration(text, "fa", anchor=ANCHOR)
    assert r is not None, "%r read no duration" % text
    assert r.duration == want
    assert r.remainder == rest
