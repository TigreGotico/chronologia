# -*- coding: utf-8 -*-
"""nl: fused relative-day/weekday + day-part compounds.

Dutch writes a relative day or weekday together with a day-part as ONE word
("morgenochtend", "woensdagmiddag"), unlike English's two-word "tomorrow
morning". The engine already reads the space-separated spelling ("morgen
ochtend"); this file asserts the fused spelling resolves to the exact same
span, for every stem the tokenizer now splits:

* relative days: "morgen" (tomorrow), "gister-" (yesterday, citation form
  "gisteren"), "overmorgen" (day after tomorrow)
* weekdays: any of the seven weekday names
* day-parts: "ochtend" [06:00, 12:00), "avond" [18:00, 24:00), "nacht"
  [00:00, 06:00), and "middag" -- which, per ``test_nl_daypart.py``, is this
  locale's word for the bare NOON INSTANT rather than a [12:00, 18:00) band,
  so a "-middag" compound resolves to that instant exactly like the
  space-separated "<day> middag" already does.

"vanmiddag" is deliberately left unparsed: "middag" carries no band
vocabulary in this locale by design (it is reserved for the noon instant),
so there is no band reading for "van" + "middag" to compose into.

Anchor: Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import ANCHOR, AstroDate, parse, span  # noqa: F401

from chronologia.extract import extract_recurrence


def _instant(y, m, d, h, mi):
    return AstroDate(y, m, d, h, mi), AstroDate(y, m, d, h, mi + 1)


_BANDS = [
    # relative-day + day-part
    ('morgenochtend', AstroDate(2017, 6, 28, 6, 0), AstroDate(2017, 6, 28, 12, 0)),
    ('morgenavond', AstroDate(2017, 6, 28, 18, 0), AstroDate(2017, 6, 29)),
    ('gisterochtend', AstroDate(2017, 6, 26, 6, 0), AstroDate(2017, 6, 26, 12, 0)),
    ('gisteravond', AstroDate(2017, 6, 26, 18, 0), AstroDate(2017, 6, 27)),
    ('overmorgenochtend', AstroDate(2017, 6, 29, 6, 0), AstroDate(2017, 6, 29, 12, 0)),
    # today + day-part ("van" fused synonyms, not a split compound)
    ('vanmorgen', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('vannacht', AstroDate(2017, 6, 27, 0, 0), AstroDate(2017, 6, 27, 6, 0)),
    # weekday + day-part
    ('maandagochtend', AstroDate(2017, 7, 3, 6, 0), AstroDate(2017, 7, 3, 12, 0)),
    ('vrijdagavond', AstroDate(2017, 6, 30, 18, 0), AstroDate(2017, 7, 1)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_compound_band(text, start, end):
    s = span(text)
    assert (s.start, s.end) == (start, end), f"{text!r} resolved to {s}"


_INSTANTS = [
    # "-middag" compounds resolve to the noon instant, exactly like the
    # already-supported space-separated "<day> middag" spelling.
    ('morgenmiddag', *_instant(2017, 6, 28, 12, 0)),
    ('gistermiddag', *_instant(2017, 6, 26, 12, 0)),
    ('woensdagmiddag', *_instant(2017, 6, 28, 12, 0)),
]


@pytest.mark.parametrize("text,start,end", _INSTANTS)
def test_compound_noon_instant(text, start, end):
    s = span(text)
    assert (s.start, s.end) == (start, end), f"{text!r} resolved to {s}"


def test_vanmiddag_stays_unparsed():
    """"middag" has no band reading in this locale (reserved for the noon
    instant), so "vanmiddag" has nothing to compose into and must not parse."""
    assert parse('vanmiddag') is None


def test_full_composition_with_clock_time():
    """The compound composes with a following clock time exactly as the
    split spelling does: the day-part is dead weight once an exact hour is
    given, and the whole compound is consumed (empty remainder)."""
    r = parse('morgenochtend om 9 uur')
    assert r is not None
    assert (r[0].start, r[0].end) == (
        AstroDate(2017, 6, 28, 9, 0), AstroDate(2017, 6, 28, 9, 1))
    assert r[1] == ''


def test_recurrence_weekday_daypart_compound():
    """"elke woensdagmiddag" behaves like the split "elke woensdag middag":
    BYDAY binds the weekday and BYHOUR binds the noon instant -- the same
    convention the space-separated spelling already uses, not a new one."""
    got = extract_recurrence('elke woensdagmiddag', 'nl', anchor=ANCHOR)
    assert got is not None
    assert got[0].to_string() == 'FREQ=WEEKLY;BYDAY=WE;BYHOUR=12'
    assert got[1] == ''


@pytest.mark.parametrize("text", [
    '',
    '   ',
    'morgenstond',
    'goedemorgen',
    'ochtend',
    'gister',
])
def test_adversarial_never_raises(text):
    """Garbage and words that merely CONTAIN a stem/day-part substring
    (never the whole token) must be survivable: nothing here may raise, and
    a partial-match word like "morgenstond" must not be split."""
    parse(text)


def test_morgenstond_is_not_split():
    """"morgenstond" starts with "morgen" but its tail ("stond") is not a
    known day-part, so the whole-token match must refuse to split it."""
    assert parse('morgenstond') is None
