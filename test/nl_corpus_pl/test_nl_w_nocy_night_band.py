"""Polish "w nocy" after an hour is a night band that crosses midnight.

"noc" is "okres od zmierzchu do świtu" (pl.wiktionary, s.v. noc, sense 1.1),
so "o drugiej w nocy" is 02:00 and "o 11 w nocy" is 23:00.  At the 13:04
anchor, 23:00 is still ahead today and 02:00 falls on 28 June.
"""
import pytest

from ._corpus import ANCHOR, ad, parse


def _at(day, hour):
    return ad(ANCHOR.replace(day=day, hour=hour, minute=0, second=0,
                             microsecond=0))


@pytest.mark.parametrize("text,day,hour", [
    ("o 11 w nocy", 27, 23),
    ("o drugiej w nocy", 28, 2),
    ("o 7 rano", 28, 7),
])
def test_night_band(text, day, hour):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(day, hour)
    assert r.remainder == ""
