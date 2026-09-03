"""Finnish day-part words: the adessive of each part of the day.

CLDR 47's fi day-period rules cut the day into five bands -- aamu 05-10,
aamupäivä 10-12, iltapäivä 12-18, ilta 18-23, yö 23-05 -- and Finnish names
each one with the adessive of its noun (aamu -> aamulla), which is the form a
speaker uses adverbially.  The locale shipped none of them, so every one of
these returned nothing.

Postposed after a clock the same word is the meridiem ("kello 9 illalla" is
21:00), and it must be CONSUMED there, not left in the remainder.

Anchor: Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import ANCHOR, ad, parse


def _at(d, h, mi=0):
    return ad(ANCHOR.replace(day=d, hour=h, minute=mi, second=0,
                             microsecond=0))


def _consumed(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r[1] == "", f"{text!r} stranded {r[1]!r}"
    return r[0]


# (text, start day/hour, end day/hour) -- the CLDR 47 fi bands on the anchor day
@pytest.mark.parametrize("text,sd,sh,ed,eh", [
    ("aamulla", 27, 5, 27, 10),
    ("aamupäivällä", 27, 10, 27, 12),
    ("iltapäivällä", 27, 12, 27, 18),
    ("illalla", 27, 18, 27, 23),
    ("yöllä", 27, 23, 28, 5),
])
def test_bare_daypart_band(text, sd, sh, ed, eh):
    s = _consumed(text)
    assert (s.start, s.end) == (_at(sd, sh), _at(ed, eh))


def test_daypart_narrows_a_named_day():
    s = _consumed("eilen illalla")
    assert (s.start, s.end) == (_at(26, 18), _at(26, 23))


def test_daypart_narrows_tomorrow():
    s = _consumed("huomenna aamulla")
    assert (s.start, s.end) == (_at(28, 5), _at(28, 10))


@pytest.mark.parametrize("text,d,h", [
    ("kello 9 illalla", 27, 21),      # 21:00 > 13:04 -> today
    ("kello 21 illalla", 27, 21),     # the 24-hour hour agrees with the band
    ("kello 9 aamulla", 28, 9),       # 09:00 < 13:04 -> tomorrow
    ("kello 3 yöllä", 28, 3),         # the night band holds the small hours
    ("kello 11 aamupäivällä", 28, 11),
    ("kello 15 iltapäivällä", 27, 15),
])
def test_clock_with_postposed_daypart(text, d, h):
    s = _consumed(text)
    assert s.start == _at(d, h)


def test_clock_contradicting_its_daypart_declines():
    """15:00 is not in the evening band, so the pair names no time -- the
    refusal a contradictory hour-plus-meridiem already gets."""
    assert parse("kello 15 illalla") is None


def test_dotted_clock_with_daypart():
    s = _consumed("klo 9.15 aamulla")
    assert s.start == _at(28, 9, 15)
