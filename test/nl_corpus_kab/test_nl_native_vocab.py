# -*- coding: utf-8 -*-
"""Kabyle forms supplied by a native speaker.

The vocabulary in this file comes from a native Kabyle speaker
(athmanemokraoui), who supplied seven date vocabulary files. His forms are
the first lines of ``locale/kab/months.voc``, ``unit_day.voc``,
``unit_year.voc``, ``season_winter.voc``, ``season_spring.voc``,
``era_year_ref.voc`` and ``marker_last.voc``.

Three of his forms were new to the locale:

* ``duǧembeṛ``, a second spelling of December beside ``dujembeṛ``. Before it
  was added to ``month_12.voc`` and ``month_berber_12.voc`` both "duǧembeṛ
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

``era_year_ref.voc`` is read by the eras subsystem, not by the span loader,
so it is carried as he wrote it and only its file content is asserted.

Gold from independent arithmetic against anchor Tue 2017-06-27.
"""
import pytest

from chronologia.extract.loader import load_lang_spec

from ._corpus import (AstroDate, LANG, nomatch, span, start, start_end)

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
# era_year_ref.voc: carried as supplied, read by the eras subsystem
# --------------------------------------------------------------------- #

def test_era_year_ref_file_carries_his_two_surfaces():
    from pathlib import Path

    import chronologia

    path = (Path(chronologia.__file__).parent / "locale" / LANG
            / "era_year_ref.voc")
    lines = [ln.strip() for ln in
             path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert lines[:2] == ["aseggas n", "deg useggas n"]


# --------------------------------------------------------------------- #
# The second batch: ten more files from the same speaker
# --------------------------------------------------------------------- #
# athmanemokraoui supplied ten more files on 2026-09-22
# (OpenVoiceOS/ovos-localize#594-#603): the seven abbreviated weekday names,
# the month unit, the year unit again and the day before yesterday. The year
# unit repeats what he already gave, byte for byte, so nine files are new.
#
# Gold from the same independent arithmetic: the anchor Tue 2017-06-27, so
# the day before yesterday is Sun 2017-06-25, and the month before the
# anchor month is May 2017.


@pytest.mark.parametrize("surface,index", [
    ("ari", 0), ("ara", 1), ("aha", 2), ("amh", 3),
    ("sem", 4), ("sed", 5), ("ace", 6),
])
def test_weekday_abbreviations_load(surface, index):
    assert SPEC.weekdays[surface] == index


@pytest.mark.parametrize("surface", ["ari", "ara", "aha", "amh",
                                     "sem", "sed", "ace"])
def test_an_abbreviation_never_reads_as_a_bare_weekday(surface):
    """A three-letter form binds the WEEKDAY slot, never the bare order.

    The loader keeps abbreviations out of ``weekday_full`` so a short form
    that is also a common word cannot resolve to a weekday on its own. This
    asserts the policy holds for his forms, and it is why the tests below
    read each abbreviation through a marker.
    """
    assert surface not in SPEC.weekday_full
    nomatch(surface)


@pytest.mark.parametrize("abbrev,full,day", [
    ("ari", "letnayen", 26),
    ("ara", "ttlata", 27),
    ("aha", "laṛebɛa", 21),
    ("amh", "lexmis", 22),
    ("sem", "lǧemɛa", 23),
    ("sed", "ssebt", 24),
    ("ace", "lḥedd", 25),
])
def test_an_abbreviation_reads_the_day_its_full_name_reads(abbrev, full, day):
    """Each abbreviation picks the same day as the locale's own full name.

    Read through the "since" marker, because the bare order refuses an
    abbreviation. The anchor is Tue 2017-06-27, so "since Monday" is
    Mon 2017-06-26 and "since Wednesday" the Wednesday before it, 21 June.
    """
    assert start("seg %s" % abbrev) == AstroDate(2017, 6, day)
    assert start("seg %s" % full) == AstroDate(2017, 6, day)


@pytest.mark.parametrize("surface", ["ayyuren", "ayyur"])
def test_month_unit_surfaces(surface):
    assert SPEC.units[surface] == "month"


@pytest.mark.parametrize("marker", ["yezrin", "iɛeddan", "aneggaru"])
def test_last_month_is_the_month_before_the_anchor(marker):
    """The month unit reaches the same ``rel_period`` order the year unit did.

    ``kab`` carried no month unit, so ``REL_MARKER UNIT`` could never match
    on a month. Anchor June 2017, so the month before it is May 2017.
    """
    s, e = start_end("%s ayyur" % marker)
    assert s == AstroDate(2017, 5, 1)
    assert e == AstroDate(2017, 6, 1)


@pytest.mark.parametrize("surface", ["send iḍelli", "sendiḍelli"])
def test_the_day_before_yesterday(surface):
    """Anchor Tue 2017-06-27, so the day before yesterday is Sun 2017-06-25."""
    s, e = start_end(surface)
    assert s == AstroDate(2017, 6, 25)
    assert e == AstroDate(2017, 6, 26)


@pytest.mark.parametrize("surface", ["send iḍelli", "sendiḍelli"])
def test_the_day_before_yesterday_is_not_yesterday(surface):
    """The control for the pair above: ``-2`` is a day before ``-1``.

    ``iḍelli`` is the locale's own yesterday and reads 26 June. A
    ``named_day_-2.voc`` read at the wrong offset, or a longest-match that
    let ``iḍelli`` win inside ``send iḍelli``, would return that date here.
    """
    assert SPEC.named_days[surface] == -2
    assert start(surface) != start("iḍelli")
