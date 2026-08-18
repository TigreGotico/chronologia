"""Serbian spoken clock, both scripts.

Three shapes: the bare "half toward the coming hour" ("pola četiri" == 3:30,
NEVER 4:30 -- adversarially pinned below), the additive "hour AND quarter"
("dva i četvrt" == 2:15), and the subtractive "quarter/minutes TO the named
hour" ("četvrt do tri" == 2:45, "petnaest do sedam" == 6:45).  No bare
"i petnaest" is attested, so it is refused rather than guessed.

Sources: Wikipedia "Date and time notation in Serbia"; gospeakserbian;
Talkpal "Telling Time in Serbian" -- cross-sourced per
lang-research/sr.md.
"""
from datetime import timedelta

import pytest

from chronologia.extract.numfold_slavic import sr_lat2cyr

from ._corpus import ANCHOR, ad, nomatch, start


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
