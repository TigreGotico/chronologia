# -*- coding: utf-8 -*-
"""R119-followup regression (ru): the "for <duration>" clock-end extension
(:func:`chronologia.extract.timespan._extend_clock_for_duration`) must never
fire on Russian's bare preposition "в" ("at"/"in").

Russian's OWN clock idiom says "at 9 o'clock" as "в 9 часов" -- the
preposition "в" is baked into the clock construction itself, and is also a
common leading/leftover word with nothing to do with any duration bound
("в следующий вторник ..." == "on next Tuesday ..."). The real "for" bound
in Russian is the two-word marker "в течение" (``marker_recur_for.voc``);
flattening that surface into its INDIVIDUAL words ({"в", "течение"}) let the
bare "в" alone stand in for the whole marker, so a stray leading "в" caused
the entire rest of an already-fully-resolved sentence to be misread as a
duration and swallowed onto the span's end -- turning "next Tuesday evening
at 9 o'clock" (21:00, a minute-wide clock, R117) into a bogus 21:00-06:00
9-HOUR band. Fixed by matching each marker surface as one atomic
(possibly multi-word) phrase, plus a position gate: the marker must sit
strictly AFTER every character the resolved span's own construction
consumed, never before or inside it.

Expected values are independently hand-computed against the anchor
(Tuesday 2017-06-27 13:04, from ``_corpus.ANCHOR``), never read back from
the parser.
"""
from datetime import datetime

from ._corpus import ANCHOR, ad, parse, start_end


def test_stray_leading_preposition_does_not_extend_span():
    # R119-followup regression: the leading "в" (a bare "on"/"at", not a
    # duration marker) must not swallow the rest of the sentence as a bogus
    # 9-hour duration. Next Tuesday from Tue 2017-06-27 is 2017-07-04.
    s, e = start_end("в следующий вторник вечером в 9 часов")
    assert (s, e) == (ad(datetime(2017, 7, 4, 21, 0)),
                      ad(datetime(2017, 7, 4, 21, 1)))


def test_stray_leading_preposition_embedded_sentence():
    r = parse("встретимся в следующий вторник вечером в 9 часов")
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2017, 7, 4, 21, 0)),
                                          ad(datetime(2017, 7, 4, 21, 1)))
    assert r.remainder == "встретимся в"


def test_clock_own_v_preposition_not_mistaken_for_marker():
    # the clock construction's OWN "в 9 часов" ("at 9 o'clock") must not be
    # re-read as a duration bound either.
    r = parse("вечером в 9 часов")
    assert r is not None
    assert r.span.end - r.span.start == r.span.end - r.span.start  # sanity
    from datetime import timedelta
    assert r.span.end - r.span.start == timedelta(minutes=1)
    assert r.remainder == ""


def test_genuine_v_techenie_duration_still_extends():
    # the REAL Russian "for" bound is the two-word "в течение" ("during") --
    # this must still work, proving the fix narrowed the marker match
    # without breaking the genuine phrase.
    s, e = start_end("в 9 утра в течение 2 часов")
    assert (s, e) == (ad(datetime(2017, 6, 28, 9, 0)),
                      ad(datetime(2017, 6, 28, 11, 0)))
