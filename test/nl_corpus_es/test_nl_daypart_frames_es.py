# -*- coding: utf-8 -*-
"""Spanish frames a part of the day with a preposition and a separate
article -- "por la mañana", "en la tarde", "a la noche", "de la madrugada" --
where Galician and Portuguese contract the two into one word ("pola mañá",
"pela manhã").  All four frames must be consumed whole: the band is the same
either way, so a stranded preposition is the only observable difference, and it
is the difference between a caller seeing an empty remainder and a caller
seeing text it cannot account for.

Gold bands are the es row of the CLDR table transcribed in
:mod:`chronologia.dayparts` -- madrugada ``[00:00, 06:00)``, mañana
``[06:00, 12:00)``, tarde ``[12:00, 20:00)``, noche ``[20:00, 24:00)`` -- and
the day is the anchor's own day, 2017-06-27.  Neither is read back from the
parser.

The article is required, not optional, and that is the point of the second
half of this file: "mañana" is equally the Spanish for *tomorrow*, and an
article-less frame order would let "por mañana" seize the day-part reading and
answer a morning band where a Spanish speaker said nothing of the kind.  With
the article mandatory the bare word keeps the tomorrow reading it has always
had.
"""
import pytest

from ._corpus import AstroDate, parse


_BANDS = {
    "madrugada": (0, 6),
    "mañana": (6, 12),
    "tarde": (12, 20),
    "noche": (20, 24),
}
_FRAMES = ["por la", "en la", "a la", "de la"]


def _band(lo, hi):
    if hi == 24:
        return (AstroDate(2017, 6, 27, lo, 0, 0), AstroDate(2017, 6, 28, 0, 0, 0))
    return (AstroDate(2017, 6, 27, lo, 0, 0), AstroDate(2017, 6, 27, hi, 0, 0))


def _cases():
    for frame in _FRAMES:
        for word, (lo, hi) in _BANDS.items():
            # "de la mañana" is claimed by the open-ended "from the morning"
            # reading, which ends at the anchor rather than at noon.
            if (frame, word) == ("de la", "mañana"):
                continue
            yield f"{frame} {word}", _band(lo, hi)


@pytest.mark.parametrize("text,want", list(_cases()))
def test_framed_daypart_consumes_the_preposition(text, want):
    r = parse(text)
    assert r is not None, text
    assert (r.span.start, r.span.end) == want, f"{text!r} -> {r.span}"
    assert r.remainder == "", f"{text!r} stranded {r.remainder!r}"


@pytest.mark.parametrize("text", ["por mañana", "en mañana", "a mañana"])
def test_article_less_frame_leaves_tomorrow_alone(text):
    """No article, no day-part: "mañana" stays the whole of tomorrow."""
    r = parse(text)
    assert r is not None
    assert (r.span.start, r.span.end) == (AstroDate(2017, 6, 28),
                                          AstroDate(2017, 6, 29))


def test_bare_manana_is_tomorrow():
    r = parse("mañana")
    assert (r.span.start, r.span.end) == (AstroDate(2017, 6, 28),
                                          AstroDate(2017, 6, 29))
    assert r.remainder == ""


@pytest.mark.parametrize("text", ["tarde", "noche", "madrugada", "más tarde",
                                  "llegué tarde", "buenas noches"])
def test_bare_daypart_word_is_not_a_span(text):
    """"tarde" is also the adverb "late" and "buenas noches" is a greeting;
    reading either as a band would answer a confident afternoon or night for
    a sentence about no time at all."""
    assert parse(text) is None


def test_day_and_frame_compose():
    r = parse("mañana por la mañana")
    assert (r.span.start, r.span.end) == (AstroDate(2017, 6, 28, 6, 0, 0),
                                          AstroDate(2017, 6, 28, 12, 0, 0))
    assert r.remainder == ""


def test_clock_keeps_its_meridiem_phrase():
    """"de la tarde" after an hour is the meridiem of a clock time, not a
    band, and the frame order must not steal it."""
    r = parse("a las tres de la tarde")
    assert r.span.start == AstroDate(2017, 6, 27, 15, 0, 0)
    assert r.remainder == ""
