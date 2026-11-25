# -*- coding: utf-8 -*-
"""Kabyle forms supplied by a native speaker.

The vocabulary in this file comes from a native Kabyle speaker
(athmanemokraoui), who supplied seven date vocabulary files. His forms are
the first lines of ``locale/kab/months``, ``unit_day``,
``unit_year``, ``season_winter``, ``season_spring``,
``era_year_ref`` and ``marker_last``.

Three of his forms were new to the locale:

* ``duǧembeṛ``, a second spelling of December beside ``dujembeṛ``. Before it
  was added to ``month_12`` and ``month_berber_12`` both "duǧembeṛ
  25" and "25 duǧembeṛ" returned ``None``. The pair is kept the way a
  locale keeps any two spellings of one month: both surfaces bind the same
  month number.
* ``iseggasen`` / ``aseggas``, the year unit.
* ``yezrin`` / ``iɛeddan`` / ``aneggaru``, the "last" markers.

The year unit and the "last" markers make the inherited ``rel_period`` base
order ``REL_MARKER UNIT`` reachable for the first time: ``kab`` shipped no
relative markers, so the order it gained from the base grammar could never
match. "iɛeddan aseggas" now reads last year and "iɛeddan ass" yesterday.

Word order is a separate question and this file does not answer it. Kabyle
postposes the qualifier, so "aseggas iɛeddan" is the order the morphology of
his three forms suggests, and that order returns ``None`` today because the
locale declares no postposed ``rel_period`` order. Adding one is a grammar
change that needs a native reader, so it is left to a follow-up and is not
asserted here.

``era_year_ref`` is read by the eras subsystem, not by the span loader,
so it is carried as he wrote it and only its file content is asserted.

Gold from independent arithmetic against anchor Tue 2017-06-27.
"""
import pytest

from chronologia.extract.loader import load_lang_spec

from ._corpus import AstroDate, LANG, span, start, start_end

SPEC = load_lang_spec(LANG)


# --------------------------------------------------------------------- #
# December: two spellings, one month
# --------------------------------------------------------------------- #

@pytest.mark.parametrize("text", [
    "duǧembeṛ 25",
    "25 duǧembeṛ",
    "dujembeṛ 25",
    "25 dujembeṛ",
])
def test_both_december_spellings_read_the_same_day(text):
    from datetime import timedelta
    assert start(text) == AstroDate(2017, 12, 25)
    assert span(text).width == timedelta(days=1)


# --------------------------------------------------------------------- #
# February: his spelling and the chart spelling both bind
# --------------------------------------------------------------------- #

@pytest.mark.parametrize("text", ["furar 14", "fuṛar 14"])
def test_both_february_spellings_read_the_same_day(text):
    assert start(text) == AstroDate(2018, 2, 14)


# --------------------------------------------------------------------- #
# Seasons and units: his form and the form the locale already carried
# --------------------------------------------------------------------- #

@pytest.mark.parametrize("surface", ["ccetwa", "tagrest"])
def test_winter_surfaces(surface):
    assert SPEC.seasons[surface] == "winter"


@pytest.mark.parametrize("surface", ["tafsut", "ṛṛbiɛ"])
def test_spring_surfaces(surface):
    assert SPEC.seasons[surface] == "spring"


@pytest.mark.parametrize("surface", ["ussan", "ass", "wass", "wussan"])
def test_day_unit_surfaces(surface):
    assert SPEC.units[surface] == "day"


@pytest.mark.parametrize("surface", ["iseggasen", "aseggas"])
def test_year_unit_surfaces(surface):
    assert SPEC.units[surface] == "year"


@pytest.mark.parametrize("surface", ["yezrin", "iɛeddan", "aneggaru"])
def test_last_markers_load(surface):
    assert SPEC.rel_markers[surface] == -1


# --------------------------------------------------------------------- #
# The "last" markers plus the year unit reach the base rel_period order
# --------------------------------------------------------------------- #

@pytest.mark.parametrize("marker", ["yezrin", "iɛeddan", "aneggaru"])
def test_last_year_is_the_year_before_the_anchor(marker):
    s, e = start_end("%s aseggas" % marker)
    assert s == AstroDate(2016, 1, 1)
    assert e == AstroDate(2017, 1, 1)


@pytest.mark.parametrize("marker", ["yezrin", "iɛeddan", "aneggaru"])
def test_last_day_is_the_day_before_the_anchor(marker):
    # anchor Tue 2017-06-27, so the day before is Mon 2017-06-26
    s, e = start_end("%s ass" % marker)
    assert s == AstroDate(2017, 6, 26)
    assert e == AstroDate(2017, 6, 27)


# --------------------------------------------------------------------- #
# era_year_ref: carried as supplied, read by the eras subsystem
# --------------------------------------------------------------------- #

def test_era_year_ref_carries_his_two_surfaces():
    from pathlib import Path

    import chronologia

    import json

    path = Path(chronologia.__file__).parent / "locale" / LANG / "vocab.json"
    words = json.loads(path.read_text(encoding="utf-8"))["words"]["era_year_ref"]
    assert {"aseggas n", "deg useggas n"} <= set(words)
