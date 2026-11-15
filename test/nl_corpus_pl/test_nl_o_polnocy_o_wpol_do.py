"""Polish "o północy" and "o wpół do <hour>".

"północ" is "godzina 24:00", and the clock preposition "o" takes the locative:
"o północy w starym zamku straszy duch" (pl.wiktionary, s.v. północ, sense
1.1).  The same locative means "in the north", so "na północy kraju" is not a
time.  "wpół do trzeciej" is 02:30, half toward the third hour, and "o" leads
it as it leads any clock.  At the 13:04 anchor the next midnight and the next
02:30 and 07:30 fall on 28 June.
"""
import pytest

from ._corpus import ANCHOR, ad, nomatch, parse


def _at(day, hour, minute):
    return ad(ANCHOR.replace(day=day, hour=hour, minute=minute, second=0,
                             microsecond=0))


@pytest.mark.parametrize("text,day,hour,minute,remainder", [
    ("o północy", 28, 0, 0, ""),
    ("przyjdź o północy", 28, 0, 0, "przyjdź"),
    ("o wpół do trzeciej", 28, 2, 30, ""),
    ("spotkajmy się o wpół do ósmej", 28, 7, 30, "spotkajmy się"),
])
def test_clock_with_o(text, day, hour, minute, remainder):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(day, hour, minute)
    assert r.remainder == remainder


def test_north_is_not_midnight():
    nomatch("na północy kraju")
