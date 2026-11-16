"""Regression for defect R130 (de half): the leading preposition "am" before
a weekday+clock composition was stranded as unconsumed remainder
("am Dienstag um 9 Uhr" -> 09:00-09:01 span, remainder "am").

"am" is the contraction "an dem" ("at/on the"), functioning exactly like a
definite article before a weekday -- the same role Romance "el"/"le"/"il"
play (Italian already lists analogous contractions -- "al", "nel", "del" --
in its own ``marker_article.voc``).  The article-swallowing composer in
``chronologia/extract/timespan.py`` (``_composition_glue``) already absorbs a
LEADING article that opens the earlier of two composing matches (Spanish
"el martes a las 9" consumes "el" this way); it never fired for German
because "am" lived only in ``marker_on.voc`` (the "on"-connector class used
by the RRULE placement qualifier, e.g. "every 2 weeks on Tuesday" ->
``ctx.on_words``), not in the "article" connector class the composer reads.
The fix adds "am" to ``chronologia/locale/de/marker_article.voc`` as well
(keeping it in ``marker_on.voc`` too, so the recurrence "on"-qualifier path
is untouched).

A lone weekday ("am Dienstag"), daypart ("am Morgen") or calendar date
("am 3. März") has nothing to compose with, so the composer does not fire.
"am" is listed in ``marker_date_lead.voc`` as the word that opens a date, and
that vocabulary takes it into the date there.

Anchor for extract_timespan cases is the shared de corpus anchor,
2017-06-27 13:04 (Tuesday) -- see ``test/nl_corpus_de/_corpus.py``.
"""
from ._corpus import ANCHOR, parse, span


# -- clean remainder: "am" fully consumes when weekday composes with clock --

def test_am_weekday_clock():
    r = parse("am Dienstag um 9 Uhr")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (9, 0)
    assert remainder == ""


def test_am_weekday_clock_other_hour():
    r = parse("am Montag um 15 Uhr")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert remainder == ""


def test_am_weekday_clock_embedded_in_sentence():
    r = parse("das Meeting ist am Dienstag um 9 Uhr im Büro")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (9, 0)
    assert "am" not in remainder.split()


def test_daypart_variant_stays_clean():
    # No "am" in this sentence at all -- confirms the daypart composition
    # path was never the leaking one.
    r = parse("Dienstag Abend um 9 Uhr")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (21, 0)
    assert remainder == ""


# -- "am" before a lone daypart, date or weekday goes with it -----------------

def test_am_goes_with_a_lone_daypart():
    r = parse("am Morgen")
    assert r is not None
    s, remainder = r
    assert remainder == ""


def test_am_goes_with_a_lone_calendar_date():
    r = parse("am 3. März")
    assert r is not None
    s, remainder = r
    assert remainder == ""


def test_am_goes_with_a_lone_weekday():
    r = parse("am Dienstag")
    assert r is not None
    s, remainder = r
    assert remainder == ""
