"""Hungarian "éjjel" before an hour is a night band that crosses midnight.

"éjjel" is "at night" (en.wiktionary, s.v. éjjel), and hu.wikipedia prose
writes "ejjel 11-kor" for 23:00, so "éjjel 2-kor" is 02:00.  At the 13:04
anchor, 23:00 is still ahead today and 02:00 falls on 28 June.
"""
import pytest

from ._corpus import ANCHOR, ad, parse


def _at(day, hour):
    return ad(ANCHOR.replace(day=day, hour=hour, minute=0, second=0,
                             microsecond=0))


@pytest.mark.parametrize("text,day,hour", [
    ("éjjel 2-kor", 28, 2),
    ("éjjel 11-kor", 27, 23),
    ("este 8-kor", 27, 20),
])
def test_night_band(text, day, hour):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(day, hour)
    assert r.remainder == ""
