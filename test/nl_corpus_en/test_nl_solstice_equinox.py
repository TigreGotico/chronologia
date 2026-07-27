"""Solstices and equinoxes resolve to their astronomical DAY, not the season.

These are location-independent astronomical instants (unlike sunrise/sunset,
which need coordinates and are deliberately unsupported), so a season-qualified
"solstice"/"equinox" resolves to the specific cardinal-event day rather than
being swallowed by the meteorological-season resolver (which would return the
whole three-month season and strand the event word in the remainder -- the
silent-wrong this corpus pins shut).

The gold days are hand-verified against Fred Espenak / AstroPixels' published
Universal-Time equinox/solstice table (the same source
``chronologia.equinoxes`` cites, chapter 27 of Jean Meeus, *Astronomical
Algorithms*, 2nd ed.):

    2017  March equinox      Mar 20
          June solstice      Jun 21
          September equinox  Sep 22
          December solstice  Dec 21
    2000  March equinox      Mar 20

The engine returns a whole civil DAY span (midnight..next midnight) for the
event's date -- the same shape a single-day holiday returns; the minute-level
instant precision is documented in :mod:`chronologia.equinoxes`.

Prefer-future mirrors the bare-holiday rule: a bare "the <season> solstice"
picks the next occurrence ON OR AFTER the anchor date.  From the mission anchor
(Tue 2017-06-27) the June solstice (Jun 21) has already passed, so bare
"the summer solstice" is the 2018 event, while the December solstice (Dec 21)
is still ahead, so "the winter solstice" stays in 2017.  An explicit year
("summer solstice 2017") always names that year's event.

A BARE "the solstice" / "the equinox" with NO season qualifier is ambiguous
(which of the two solstices / two equinoxes?) and deliberately does not
resolve -- documented as a non-match here.
"""
from datetime import datetime

from ._corpus import AstroDate, start_end, span, nomatch


def _day(y, m, d):
    return AstroDate(y, m, d), AstroDate(y, m, d + 1)


# -- explicit year: that year's event ------------------------------------

def test_summer_solstice_explicit_year():
    assert start_end("summer solstice 2017") == _day(2017, 6, 21)


def test_winter_solstice_explicit_year():
    assert start_end("winter solstice 2017") == _day(2017, 12, 21)


def test_spring_equinox_explicit_year():
    assert start_end("spring equinox 2017") == _day(2017, 3, 20)


def test_autumn_equinox_explicit_year():
    assert start_end("autumn equinox 2017") == _day(2017, 9, 22)


# -- month-named cardinal events -----------------------------------------

def test_june_solstice():
    assert start_end("june solstice 2017") == _day(2017, 6, 21)


def test_december_solstice():
    assert start_end("december solstice 2017") == _day(2017, 12, 21)


def test_march_equinox():
    assert start_end("march equinox 2017") == _day(2017, 3, 20)


def test_september_equinox():
    assert start_end("september equinox 2017") == _day(2017, 9, 22)


# -- another year, exercising the Meeus algorithm ------------------------

def test_march_equinox_2000():
    assert start_end("the march equinox 2000") == _day(2000, 3, 20)


def test_vernal_equinox_2000():
    assert start_end("the vernal equinox 2000") == _day(2000, 3, 20)


# -- formal / alternate season names -------------------------------------

def test_vernal_equinox_explicit_year():
    assert start_end("vernal equinox 2017") == _day(2017, 3, 20)


def test_autumnal_equinox_explicit_year():
    assert start_end("autumnal equinox 2017") == _day(2017, 9, 22)


def test_fall_equinox_explicit_year():
    assert start_end("fall equinox 2017") == _day(2017, 9, 22)


# -- bare (no year): prefer-future, on-or-after the anchor ----------------

def test_bare_summer_solstice_prefers_future():
    # Jun 21 2017 already passed at the 2017-06-27 anchor -> 2018.
    assert start_end("the summer solstice") == _day(2018, 6, 21)


def test_bare_winter_solstice_still_this_year():
    # Dec 21 2017 is still ahead of the anchor -> 2017.
    assert start_end("the winter solstice") == _day(2017, 12, 21)


def test_bare_spring_equinox_prefers_future():
    # Mar 20 2017 passed -> 2018.
    assert start_end("the spring equinox") == _day(2018, 3, 20)


def test_bare_autumn_equinox_still_this_year():
    assert start_end("the autumn equinox") == _day(2017, 9, 22)


def test_bare_fall_equinox_still_this_year():
    assert start_end("the fall equinox") == _day(2017, 9, 22)


def test_bare_vernal_equinox_prefers_future():
    assert start_end("the vernal equinox") == _day(2018, 3, 20)


def test_bare_autumnal_equinox_still_this_year():
    assert start_end("the autumnal equinox") == _day(2017, 9, 22)


# -- bare, no season qualifier: ambiguous, does not resolve --------------

def test_bare_solstice_ambiguous_nomatch():
    nomatch("the solstice")


def test_bare_equinox_ambiguous_nomatch():
    nomatch("the equinox")


# -- REGRESSION: plain SEASON words still return the SEASON span ----------
# (meteorological three-month blocks, byte-identical to before this change).

def test_season_summer_unchanged():
    assert start_end("summer") == (AstroDate(2017, 6, 1), AstroDate(2017, 9, 1))


def test_season_in_the_summer_unchanged():
    assert start_end("in the summer") == (AstroDate(2017, 6, 1),
                                          AstroDate(2017, 9, 1))


def test_season_next_winter_unchanged():
    assert start_end("next winter") == (AstroDate(2017, 12, 1),
                                        AstroDate(2018, 3, 1))


def test_season_spring_unchanged():
    assert start_end("spring") == (AstroDate(2017, 3, 1), AstroDate(2017, 6, 1))


def test_season_autumn_unchanged():
    assert start_end("autumn") == (AstroDate(2017, 9, 1),
                                   AstroDate(2017, 12, 1))


def test_season_fall_unchanged():
    assert start_end("fall") == (AstroDate(2017, 9, 1), AstroDate(2017, 12, 1))
