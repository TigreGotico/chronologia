"""Ukrainian "ночі" is a night band, and "об" is "о" before a vowel.

СУМ-11 gives "ніч" as "Частина доби від заходу до сходу сонця, з вечора до
ранку", so "о 2 ночі" is 02:00 and "о 11 ночі" is 23:00.  "об" names the hour
"тільки перед голосним" (СУМ-11, s.v. об, sense 1, "об 11 годині").  At the
13:04 anchor, 23:00 is still ahead today; 02:00 and 11:00 fall on 28 June.
"""
import pytest

from ._corpus import ANCHOR, ad, parse


def _at(day, hour):
    return ad(ANCHOR.replace(day=day, hour=hour, minute=0, second=0,
                             microsecond=0))


@pytest.mark.parametrize("text,day,hour", [
    ("о 2 ночі", 28, 2),
    ("о 11 ночі", 27, 23),
    ("об 11 ночі", 27, 23),
    ("об 11", 28, 11),
    ("об одинадцятій", 28, 11),
    ("о 7 ранку", 28, 7),
])
def test_night_band_and_ob(text, day, hour):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(day, hour)
    assert r.remainder == ""
