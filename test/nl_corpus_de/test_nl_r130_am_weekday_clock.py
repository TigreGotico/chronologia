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

Bare "am Dienstag" (a single, uncomposed ``weekday_ref`` match -- nothing to
compose with) is UNCHANGED by this fix: the composer only fires when two
matches actually fuse, so a lone weekday match still has no order that
accepts a leading "am" for itself. Likewise a lone daypart ("am Morgen") or a
lone calendar date ("am 3. März") -- neither composes with anything else in
those sentences -- keep leaking "am" exactly as before.

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


# -- controls: "am" elsewhere, with nothing to compose with, is unchanged ---

def test_am_morgen_control_unchanged():
    r = parse("am Morgen")
    assert r is not None
    s, remainder = r
    assert remainder == "am"


def test_am_calendar_date_control_unchanged():
    r = parse("am 3. März")
    assert r is not None
    s, remainder = r
    assert remainder == "am"


def test_bare_am_weekday_control_unchanged():
    # A lone weekday_ref -- no composition, no order accepts a leading "am".
    r = parse("am Dienstag")
    assert r is not None
    s, remainder = r
    assert remainder == "am"
