"""R186 (fa): the Persian additive clock fraction "<hour> و <quarter/half>"
(HOUR CLOCKDIR FRACTION) was entirely unwired -- the bare hour ("ساعت دو")
already resolved, but "دو و ربع"/"دو و نیم" returned no match at all.

Direction is a fact of the language, not a guess: Persian "و" ("and") counts
the fraction PAST the stated hour, the opposite convention from a
toward-the-next-hour system.  Two independent worked examples confirm this:
  - UT Austin, Persian Online Resources, "To Tell the Time":
    "sa'at yek-o rob' ast" == "It is one-fifteen" and "sa'at do-vo nim ast"
    == "It is two-thirty."
    https://sites.la.utexas.edu/persian_online_resources/numbers-1/to-tell-the-time/
  - talkpal.ai, "Telling Time in Persian Language": "3:15 - sa'at-e seh va
    rob'" and "4:30 - sa'at-e chahar va nim".
    https://talkpal.ai/vocabulary/telling-time-in-persian-language/

Golds below are computed by hand from the 2017-06-27 13:04 Tuesday anchor
with ``prefer_future``: any wall time already passed today rolls to the next
day, 2017-06-28.
"""
from datetime import timedelta

from ._corpus import ANCHOR, ad, parse


def test_bare_hour():
    # "ساعت دو" == at two o'clock == 02:00, the hour the fractions below are
    # built from.
    r = parse("ساعت دو")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=2, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""


def test_quarter_past_names_the_stated_hour():
    # "دو و ربع" == two and a quarter == 02:15 -- PAST the stated hour, not
    # 15 minutes before it (a "to"-direction reading would land on 01:45,
    # a full 30 minutes off the correct reading, catching a reversed
    # implementation loudly).
    r = parse("دو و ربع")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=2, minute=15,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""


def test_half_past_names_the_stated_hour():
    # "دو و نیم" == two and a half == 02:30, sitting a full hour after the
    # bare "ساعت سه" == 03:00 below, so a reversed (toward-next-hour)
    # direction that would read this as 01:30 fails loudly against that
    # pairing.
    r = parse("دو و نیم")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=2, minute=30,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""


def test_next_bare_hour_pairs_against_half_past():
    # "ساعت سه" == at three o'clock == 03:00, a full 30 minutes after
    # "دو و نیم" == 02:30 above -- the adversarial pin that a
    # toward-the-hour misreading of "و" would collapse the two together.
    r = parse("ساعت سه")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=3, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""
