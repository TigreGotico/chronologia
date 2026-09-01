"""Serbian spoken clock, both scripts.

Three shapes: the bare "half toward the coming hour" ("pola četiri" == 3:30,
NEVER 4:30 -- adversarially pinned below), the additive "hour AND quarter"
("dva i četvrt" == 2:15), and the subtractive "quarter/minutes TO the named
hour" ("četvrt do tri" == 2:45, "petnaest do sedam" == 6:45).

The additive minute count IS attested -- gospeakserbian's "How To Tell Time
in Serbian" prints "08:15 osam i petnaest", "08:20 osam i dvadeset" and
"pet sati i trideset tri minuta -- 05:33", and Omniglot gives "Сада је један
и петнаест" for 1:15 -- but it is NOT read, and the reason is recorded in the
strict xfails at the end of this file.  Serbian joins its compound numerals
with the same "i", and the clock slots accept cardinals and ordinals alike,
so any order that reads "HOUR i MINUTE" also reads "dvadeset i pet" (the
numeral 25) and "osmog i devetog maja" (the 8th and 9th of May) as times of
day.  Separating them needs a slot that can reject an ordinal-marked token,
which the grammar cannot currently express.

Sources: Wikipedia "Date and time notation in Serbia"; gospeakserbian;
Talkpal "Telling Time in Serbian" -- cross-sourced per
lang-research/sr.md.
"""
from datetime import timedelta

import pytest

from chronologia.extract.numfold_slavic import sr_lat2cyr

from ._corpus import ANCHOR, ad, nomatch, remainder, start


def _cyr(phrase: str) -> str:
    return " ".join(sr_lat2cyr(w) for w in phrase.split())


@pytest.mark.parametrize("phrase,hour,minute", [
    ("pola četiri", 3, 30),
    ("pola sedam", 6, 30),
    ("pola jedan", 12, 30),   # toward-hour 12h wrap: half toward one is 12:30
    ("dva i četvrt", 2, 15),
    ("sedam i četvrt", 7, 15),
    ("četvrt do tri", 2, 45),
    ("četvrt do jedan", 12, 45),
    ("petnaest do sedam", 6, 45),
])
def test_clock_latin(phrase, hour, minute):
    base = ANCHOR.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if base < ANCHOR:
        base = base + timedelta(days=1)
    assert start(phrase) == ad(base)


@pytest.mark.parametrize("phrase,hour,minute", [
    ("pola četiri", 3, 30), ("dva i četvrt", 2, 15),
    ("četvrt do tri", 2, 45), ("petnaest do sedam", 6, 45),
])
def test_clock_cyrillic(phrase, hour, minute):
    base = ANCHOR.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if base < ANCHOR:
        base = base + timedelta(days=1)
    assert start(_cyr(phrase)) == ad(base)


def test_pola_cetiri_is_never_four_thirty():
    """Adversarial: "pola" names the hour it counts TOWARD, not the hour it
    follows -- "pola četiri" is 3:30, never 4:30."""
    got = start("pola četiri")
    assert got != ad(ANCHOR.replace(hour=4, minute=30, second=0,
                                    microsecond=0) + timedelta(days=1))
    assert got == ad(ANCHOR.replace(hour=3, minute=30, second=0,
                                    microsecond=0) + timedelta(days=1))


def test_bare_i_petnaest_is_unattested():
    """No bare "i petnaest" ("and fifteen") clock idiom is attested for
    Serbian -- refused rather than guessed as quarter-past."""
    nomatch("sedam i petnaest")


def test_bare_quarter_is_unattested():
    """A bare quarter with no direction word ("četvrt sedam") is not the
    Serbian idiom (unlike the additive bare half) -- refused."""
    nomatch("četvrt sedam")


# -- bare "N o'clock": the marker inflects like the unit ---------------------

@pytest.mark.parametrize("phrase,hour", [
    ("jedan sat", 1), ("dva sata", 2), ("tri sata", 3), ("pet sati", 5),
    ("један сат", 1), ("два сата", 2), ("пет сати", 5),
])
def test_bare_oclock_across_the_paucal_classes(phrase, hour):
    """The bare "o'clock" word inflects with the hour count exactly like
    the duration unit ("jedan sat", "dva sata", "pet sati") -- consistent
    across 1 / 2-4 / 5+, not just the genitive-plural class."""
    base = ANCHOR.replace(hour=hour, minute=0, second=0, microsecond=0)
    if base <= ANCHOR:
        base = base + timedelta(days=1)
    assert start(phrase) == ad(base)


# -- the leading preposition is consumed, not stranded -----------------------

@pytest.mark.parametrize("phrase,hour,minute", [
    ("u pola devet", 8, 30),
    ("na pola devet", 8, 30),
    ("u dva i četvrt", 2, 15),
    ("u četvrt do tri", 2, 45),
    ("u petnaest do sedam", 6, 45),
    ("у пола девет", 8, 30),
    ("у два и четврт", 2, 15),
])
def test_the_at_preposition_is_consumed_by_every_fraction_order(phrase, hour, minute):
    """Every hour-only order already admits the "at" preposition; the four
    fraction orders did not, so "u pola devet" gave the right minute with
    "u" left standing in the remainder.  Slovenian ships the same shape as
    "at? FRACTION HOUR ...".  gospeakserbian prints "u pola devet ujutru"."""
    base = ANCHOR.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if base <= ANCHOR:
        base = base + timedelta(days=1)
    assert start(phrase) == ad(base)
    # The time was already right without the preposition ordered; what was
    # wrong is that the preposition stayed behind, so the remainder is the
    # whole assertion here.
    assert remainder(phrase) == ""


# -- the additive minute count, attested but unread -------------------------

@pytest.mark.xfail(strict=True, reason=(
    "gospeakserbian prints these rows, but the clock slots accept ordinals "
    "and cardinals alike and 'i' also joins compound numerals, so an order "
    "reading HOUR i MINUTE also reads 'dvadeset i pet' (25) and 'osmog i "
    "devetog maja' (the 8th and 9th of May) as clock times"))
@pytest.mark.parametrize("phrase,hour,minute", [
    ("osam i petnaest", 8, 15),
    ("osam i dvadeset", 8, 20),
    ("osam i trideset pet", 8, 35),
    ("osam i četrdeset", 8, 40),
    ("pet sati i trideset tri minuta", 5, 33),
    ("осам и петнаест", 8, 15),
])
def test_the_additive_minute_count_is_attested_but_unread(phrase, hour, minute):
    base = ANCHOR.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if base <= ANCHOR:
        base = base + timedelta(days=1)
    assert start(phrase) == ad(base)


@pytest.mark.parametrize("phrase", [
    "dvadeset i pet", "dvadeset i jedan", "dvadeset i pet godina",
    "za dvadeset i pet minuta", "trideset i deset", "pedeset i jedan",
    "20 i 5", "двадесет и пет",
])
def test_a_compound_numeral_is_never_a_clock_time(phrase):
    """The counterweight to the xfail above: "i" joining a compound numeral
    must never be read as the clock's additive connector.  Reading "dvadeset
    i pet godina" ("twenty-five years") as 20:05 is the failure mode that
    kept this construction out."""
    nomatch(phrase)


@pytest.mark.parametrize("phrase", [
    "od osam do devet", "osam do devet", "osam do pet", "od dva do pet",
    "од осам до девет",
])
def test_a_direction_word_never_names_the_hour_first(phrase):
    """"do" is both the subtractive direction word and the range terminator,
    so an hour-first order accepting it reads "from eight to nine" as eight
    minutes to nine.  Refusal is the contract."""
    nomatch(phrase)
