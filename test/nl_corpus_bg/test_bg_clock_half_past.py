# -*- coding: utf-8 -*-
"""Bulgarian additive-past half hour: "осем и половина" == "eight and a
half" == 08:30, spoken PAST the stated hour -- the opposite direction from
the toward-hour Slovene/Croatian/Czech "pol"/"pola"/"půl" siblings ("pol
devetih"/"pola devet"/"půl deváté" == half TOWARD nine == 08:30 too, but by
naming the coming hour, not the one just past).

Two independent attestations of the Bulgarian direction, each with a worked
numeric example:
  en.wikibooks.org/wiki/Bulgarian/Time -- "Единайсет и трийсет, Единайсет и
    половина (Edinayset i triyset, Edinayset i polovina) = Eleven thirty,
    Half past eleven = 11:30".
  preply.com, telling the time in Bulgarian -- "Пет и половина" == 5:30,
    "Три и половина" == 3:30.

Wired via the same additive-past mechanism as Greek's "H και μισή"
(chronologia/locale/el/lang.json:30-38, clock_dir_past.voc "και" +
clock_fraction_30.voc "μισή"): clock_dir_past.voc "и" + clock_fraction_30.voc
"половина".

"половин"/"половина" also spell the calendar half ("първата половина на
2020"); the clock reading below is pinned adversarially beside the plain
hour it is built from, thirty minutes apart, with the plain hour asserted
against an absolute literal so a test comparing two parser outputs can never
pass while both are wrong. Anchor: Tuesday 2017-06-27 13:04.
"""
from ._corpus import start, start_end
from chronologia.astrodate import AstroDate


def test_plain_hour_is_eight_am_next_day():
    # "в осем" (at eight) rolls past the 13:04 anchor to the next morning.
    assert start("в осем") == AstroDate(2017, 6, 28, 8, 0, 0, 0)


def test_half_past_is_thirty_minutes_after_the_plain_hour():
    assert start("осем и половина") == AstroDate(2017, 6, 28, 8, 30, 0, 0)


def test_half_past_matches_the_additive_direction_not_toward_hour():
    # If the direction were toward-hour (like sl/hr/cs), "осем и половина"
    # would read as half toward eight == 07:30, not 08:30.
    assert start("осем и половина") != AstroDate(2017, 6, 28, 7, 30, 0, 0)


def test_half_past_other_hours():
    assert start("пет и половина") == AstroDate(2017, 6, 28, 5, 30, 0, 0)
    assert start("десет и половина") == AstroDate(2017, 6, 28, 10, 30, 0, 0)


def test_half_period_still_resolves_with_the_shared_half_word():
    # "половина" also spells the calendar half of a year; the clock wiring
    # above must not disturb that reading.
    s, e = start_end("първата половина на 2020")
    assert s == AstroDate(2020, 1, 1)
    assert e == AstroDate(2020, 7, 1)


def test_half_past_after_the_at_preposition_and_with_a_daypart():
    # "в" ("at") introduces every other spoken hour in this locale; without
    # its own sibling order the half-past reading left the preposition
    # standing in the remainder.
    assert start("в шест и половина сутринта") == AstroDate(2017, 6, 28, 6, 30, 0, 0)
