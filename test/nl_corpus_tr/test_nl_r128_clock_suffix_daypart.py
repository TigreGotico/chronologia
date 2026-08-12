# -*- coding: utf-8 -*-
"""R128: Turkish apostrophe-suffixed clock hours and possessive day-parts.

Two related silent-wrong defects on the "<weekday> [<daypart>] saat
<hour>'<locative>" construction:

1. A digit clock hour with the locative case spelled with an apostrophe
   ("9'da", "9'te" -- as opposed to the spelled-out "dokuzda") strands the
   suffix ("da"/"te") in the remainder: ``split_contractions`` breaks the
   apostrophe into its own token boundary, so the tokenizer yields
   ["9", "da"] rather than one glued word, and the digit path never got the
   locative-strip the word-form spoken-clock path already has
   (``numfold_turkic._strip_locative_hour``).

2. The 3rd-person possessive day-part forms ("akşamı" = "its evening" / "the
   evening of <day>", "sabahı" = "its morning") were absent from the tr
   day-part vocab (only the bare "akşam"/"sabah" were listed), so
   "salı akşamı saat 9'da" ("Tuesday evening at 9") never matched a DAYPART
   slot at all: the whole "akşamı saat 9'da" clause fell out unbound and the
   date-only reading won, SILENTLY DROPPING the time. With the possessive
   forms recognised, ``compose_daypart_clock`` (PR #678) can fire and fold
   the day-part into a meridiem on the clock, exactly as it already does for
   en/ru/ar ("evening at 9" -> 21:00).

Anchor: 2026-07-15 12:00 (Wednesday), per ``_corpus.ANCHOR``. The next Tuesday
from that anchor is 2026-07-21.
"""
from ._corpus import ANCHOR, nomatch, parse, span, start

TUESDAY = "2026-07-21"


def _iso(astro):
    return "%04d-%02d-%02d" % (astro.year, astro.month, astro.day)


# ---------------------------------------------------------------------------
# 1. Apostrophe-suffixed digit clock hours -- the locative marker must be
#    consumed, not stranded in the remainder.
# ---------------------------------------------------------------------------

def test_saat_9_apostrophe_da_reads_nine_empty_remainder():
    r = parse("saat 9'da")
    assert r is not None
    assert r.span.start.hour == 9
    assert r.remainder == ""


def test_saat_9_apostrophe_te_reads_nine_empty_remainder():
    # "-te" harmonises after a front-unrounded stem; both suffixes must be
    # consumed identically.
    r = parse("saat 9'te")
    assert r is not None
    assert r.span.start.hour == 9
    assert r.remainder == ""


def test_saat_10_apostrophe_da_reads_ten_empty_remainder():
    r = parse("saat 10'da")
    assert r is not None
    assert r.span.start.hour == 10
    assert r.remainder == ""


def test_saat_15_apostrophe_te_reads_fifteen_empty_remainder():
    r = parse("saat 15'te")
    assert r is not None
    assert r.span.start.hour == 15
    assert r.remainder == ""


def test_apostrophe_suffixed_matches_bare_digit_form():
    # The suffix must be a pure marker: same instant as the unsuffixed form.
    assert parse("saat 9'da") == parse("saat 9")


def test_weekday_plus_apostrophe_suffixed_clock_binds():
    r = parse("salı saat 9'da")
    assert r is not None
    assert _iso(r.span.start) == TUESDAY
    assert r.span.start.hour == 9
    assert r.remainder == ""


# ---------------------------------------------------------------------------
# 2. Possessive day-part + apostrophe-suffixed clock -- daypart-as-meridiem
#    composition (PR #678) must fire.
# ---------------------------------------------------------------------------

def test_evening_possessive_plus_clock_composes_to_pm():
    # "salı akşamı saat 9'da" = "Tuesday evening at 9" -> 21:00, not a bare
    # date with the whole clause stranded.
    r = parse("salı akşamı saat 9'da")
    assert r is not None
    assert _iso(r.span.start) == TUESDAY
    assert r.span.start.hour == 21
    assert r.remainder == ""


def test_morning_possessive_plus_clock_stays_am():
    # "salı sabahı saat 9'da" = "Tuesday morning at 9" -> 09:00 (morning
    # scopes the AM half, hour unchanged for 1..11).
    r = parse("salı sabahı saat 9'da")
    assert r is not None
    assert _iso(r.span.start) == TUESDAY
    assert r.span.start.hour == 9
    assert r.remainder == ""


def test_evening_possessive_plus_bare_digit_clock_composes_too():
    # Same composition without the apostrophe suffix, to isolate that the
    # possessive day-part fix is independent of the locative-suffix fix.
    r = parse("salı akşamı saat 9")
    assert r is not None
    assert r.span.start.hour == 21
    assert r.remainder == ""


def test_morning_possessive_alone_still_scopes_am_hour():
    # Sanity: the possessive form composes with a spelled locative-hour too
    # (not just the apostrophe digit form).
    r = parse("salı sabahı saat dokuzda")
    assert r is not None
    assert r.span.start.hour == 9
    assert r.remainder == ""


def test_embedded_sentence_evening_possessive_clock():
    r = parse("toplantı salı akşamı saat 9'da")
    assert r is not None
    assert _iso(r.span.start) == TUESDAY
    assert r.span.start.hour == 21
    assert "toplantı" in r.remainder
    assert "akşamı" not in r.remainder
    assert "9" not in r.remainder
    assert "da" not in r.remainder.split()


# ---------------------------------------------------------------------------
# Controls -- must be unaffected by either fix.
# ---------------------------------------------------------------------------

def test_evening_possessive_alone_still_gives_evening_band():
    # No clock present: "salı akşamı" alone must resolve to the Tuesday
    # evening band (19:00-21:00 per CLDR tr), fully consumed.
    r = parse("salı akşamı")
    assert r is not None
    assert _iso(r.span.start) == TUESDAY
    assert r.span.start.hour == 19
    assert r.span.end.hour == 21
    assert r.remainder == ""


def test_bare_evening_word_still_matches_unchanged():
    # The plain (non-possessive) "akşam" surface must still match.
    r = parse("salı akşam")
    assert r is not None
    assert r.remainder == ""


def test_gunu_construction_unaffected_pr671():
    # PR #671's "<weekday> günü" reading must be byte-identical.
    r = parse("salı günü")
    assert r is not None
    assert _iso(r.span.start) == TUESDAY
    assert r.remainder == ""


def test_bare_saat_9_unaffected():
    r = parse("saat 9")
    assert r is not None
    assert r.span.start.hour == 9
    assert r.remainder == ""


def test_orada_survives_unconsumed():
    # "orada" ("there") ends in "-da" but is not adjacent to any digit via
    # an apostrophe: must not be touched by the locative-suffix strip, and
    # (having no date/time content at all) must simply fail to parse.
    nomatch("orada")


def test_burada_survives_unconsumed():
    nomatch("burada")


def test_orada_in_sentence_survives_in_remainder():
    # A genuine date next to the unrelated "-da" word: "orada" must remain
    # in the remainder, not be silently eaten as if it were a clock suffix.
    r = parse("salı orada")
    assert r is not None
    assert _iso(r.span.start) == TUESDAY
    assert "orada" in r.remainder


def test_bare_number_without_saat_does_not_bind_as_clock():
    # Without the "saat" hour-noun, a bare apostrophe-suffixed digit must
    # not spuriously resolve (the locative strip is gated on "saat").
    nomatch("10'da")
