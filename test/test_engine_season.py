"""season_ref stage: hemisphere-aware meteorological seasons, next/last/this
and "of YYYY", resolved against the fixed anchor datetime(2017, 6, 27).

Meteorological seasons are month-aligned and three months wide; the
hemisphere is a lang.json convention fact.  Values cross-check the
``ranges`` season helpers the construction reuses."""
from dataclasses import replace
from datetime import datetime, timedelta

import pytest
from engine_helpers import ANCHOR, load_zz

from chronologia.astrodate import AstroDate
from chronologia.extract import DateTimeEngine


def _engine(hemisphere=None):
    spec = load_zz()
    if hemisphere:
        spec = replace(spec, conventions=replace(spec.conventions,
                                                 hemisphere=hemisphere))
    return DateTimeEngine(spec)


def _one(text, hemisphere=None, anchor=ANCHOR):
    res = _engine(hemisphere).resolve(text, anchor)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


# -- "of YYYY", width = three months ---------------------------------------

def test_summer_of_1969():
    r = _one("zsummer zof 1969")
    assert r.value.start == AstroDate(1969, 6, 1)
    assert r.value.end == AstroDate(1969, 9, 1)          # three months

def test_winter_wraps_new_year():
    r = _one("zwinter zof 1969")
    assert r.value.start == AstroDate(1969, 12, 1)
    assert r.value.end == AstroDate(1970, 3, 1)


# -- next / last / this / bare ---------------------------------------------

def test_next_summer_rolls_past_mid_season_anchor():
    # anchor 2017-06-27 is past the 2017 summer start, so *next* summer is 2018
    assert _one("znext zsummer").value.start == AstroDate(2018, 6, 1)

def test_last_summer_is_the_summer_that_ended():
    # the anchor sits inside the 2017 summer, which a speaker never calls
    # "last summer" -- the completed one is 2016's
    assert _one("zlast zsummer").value.start == AstroDate(2016, 6, 1)

def test_last_winter():
    assert _one("zlast zwinter").value.start == AstroDate(2016, 12, 1)

def test_this_summer():
    assert _one("zthis zsummer").value.start == AstroDate(2017, 6, 1)

def test_bare_summer_anchor_year():
    assert _one("zsummer").value.start == AstroDate(2017, 6, 1)


# -- deixis across the December..February winter boundary ------------------

# The wrapping season is the one that can disagree with the calendar year:
# on January 15th 2018 the winter in progress started in December 2017, so
# "this winter" names it, "last winter" the December 2016 one that is over,
# and "next winter" the December still to come.

_WINTER_ANCHOR = datetime(2018, 1, 15, 13, 4)

def test_this_winter_is_the_one_in_progress_in_january():
    assert _one("zthis zwinter", anchor=_WINTER_ANCHOR).value.start \
        == AstroDate(2017, 12, 1)

def test_last_winter_in_january_reaches_past_the_running_one():
    assert _one("zlast zwinter", anchor=_WINTER_ANCHOR).value.start \
        == AstroDate(2016, 12, 1)

def test_next_winter_in_january_is_the_december_to_come():
    assert _one("znext zwinter", anchor=_WINTER_ANCHOR).value.start \
        == AstroDate(2018, 12, 1)

def test_bare_winter_in_january_is_the_one_in_progress():
    assert _one("zwinter", anchor=_WINTER_ANCHOR).value.start \
        == AstroDate(2017, 12, 1)

def test_southern_summer_deixis_wraps_the_same_way():
    # southern summer is the December-starting season, so the January
    # reading mirrors the northern winter exactly
    assert _one("zlast zsummer", hemisphere="south",
                anchor=_WINTER_ANCHOR).value.start == AstroDate(2016, 12, 1)
    assert _one("zthis zsummer", hemisphere="south",
                anchor=_WINTER_ANCHOR).value.start == AstroDate(2017, 12, 1)
    assert _one("znext zsummer", hemisphere="south",
                anchor=_WINTER_ANCHOR).value.start == AstroDate(2018, 12, 1)


# -- hemisphere is a convention fact ---------------------------------------

def test_southern_summer_starts_december():
    r = _one("zsummer zof 1969", hemisphere="south")
    assert r.value.start == AstroDate(1969, 12, 1)
    assert r.value.end == AstroDate(1970, 3, 1)

def test_southern_spring_starts_september():
    assert _one("zspring zof 1969", hemisphere="south").value.start \
        == AstroDate(1969, 9, 1)


# -- adversarial -----------------------------------------------------------

def test_garbage_never_raises():
    _engine().resolve("zzz not a season", ANCHOR)

def test_fall_autumn_alias():
    # FALL and AUTUMN share the Season value; "fall" resolves to Sep 1
    assert _one("zfall zof 1969").value.start == AstroDate(1969, 9, 1)
