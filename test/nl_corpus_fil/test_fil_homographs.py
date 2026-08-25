"""The four temporal homographs, and what this locale does about each.

Filipino's core time vocabulary collides with ordinary nouns four times over:
``linggo`` is both Sunday and the week, ``araw`` both the day and the sun,
``buwan`` both the month and the moon, and ``makalawa`` both the day after
tomorrow and the frequency adverb "twice".  Only two of the four are
reachable as a competing TEMPORAL reading, and those two are handled
differently: ``linggo`` gets the count-conditioned veto, ``makalawa`` is not
shipped at all.
"""
import pytest

from ._corpus import nomatch, span, start


@pytest.mark.parametrize("count", ["dalawang", "tatlong", "limang",
                                   "sampung"])
def test_a_counted_linggo_refuses_rather_than_picking_a_sense(count):
    """A count before ``linggo`` is ambiguous between a span of weeks and a
    number of Sundays.  Handing back one specific Sunday to a caller who
    asked for a duration would be a worse answer than none, so the whole
    phrase declines -- and declining the weekday reading is not the same as
    asserting the week one, which this locale spells ``semana``."""
    nomatch(f"sa {count} linggo")
    nomatch(f"{count} linggo")


@pytest.mark.parametrize("count,weeks", [
    ("dalawang", 2), ("tatlong", 3), ("limang", 5),
])
def test_semana_is_the_unambiguous_week(count, weeks):
    from datetime import timedelta

    from ._corpus import ANCHOR, ad
    assert start(f"sa {count} semana") == ad(ANCHOR + timedelta(weeks=weeks))


def test_an_uncounted_linggo_is_still_sunday():
    """The veto is conditioned on the count, so the bare weekday name -- the
    only reading CLDR gives the word -- keeps working."""
    assert start("linggo").datetime().weekday() == 6
    assert start("noong linggo").datetime().weekday() == 6


@pytest.mark.parametrize("count,days", [
    ("dalawang", 2), ("tatlong", 3), ("sampung", 10),
])
def test_araw_counts_as_the_day_and_never_as_the_sun(count, days):
    """``araw`` names both the day and the sun, but the sun is not a quantity
    anything is counted in, so the two senses never compete for one reading."""
    from datetime import timedelta

    from ._corpus import ANCHOR, ad
    assert start(f"sa {count} araw") == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("count,months", [("dalawang", 2), ("limang", 5)])
def test_buwan_counts_as_the_month_and_never_as_the_moon(count, months):
    s = start(f"sa {count} buwan")
    assert (s.year, s.month) == (2017 + (6 + months) // 13,
                                 (6 + months - 1) % 12 + 1)


@pytest.mark.parametrize("text", ["araw", "buwan"])
def test_a_bare_unit_noun_names_no_date(text):
    """With nothing counting it, the word is just its noun -- day or sun,
    month or moon -- and no date can be read out of it either way."""
    nomatch(text)


@pytest.mark.parametrize("text", ["makalawa", "sa makalawa"])
def test_makalawa_is_not_shipped_as_the_day_after_tomorrow(text):
    """The same bare word is the frequency adverb "twice", the named-day
    grammar matches a day word bare, and no attested disambiguator survives
    tokenization -- so the day-after-tomorrow reading is declined rather than
    guessed, and with it the ``sa makalawa`` phrasing that would carry it."""
    nomatch(text)


def test_its_unambiguous_mirror_does_ship():
    """``kamakalawa`` carries the ``ka-`` prefix and has only the one sense,
    so the day before yesterday is available even though the day after
    tomorrow is not."""
    assert start("kamakalawa").day == 25


def test_a_relative_marker_on_linggo_reads_the_weekday():
    """Under a relative marker rather than a count, ``linggo`` resolves as
    the weekday, which is the only sense this locale gives the word: the
    week is ``semana``, and no locale data can distinguish "last week" from
    "last Sunday" on this surface."""
    assert start("nakaraang linggo").datetime().weekday() == 6
    assert start("nakaraang linggo").datetime().day == 25
