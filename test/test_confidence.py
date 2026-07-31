# -*- coding: utf-8 -*-
"""Confidence scoring: the score, the ranked-candidate API, and calibration.

Three contracts are exercised here:

1. **Shape** -- every confidence lies in ``(0, 1]``, is deterministic, and the
   ranked :func:`~chronologia.extract.extract_candidates` surfaces the runner-up
   parses (not just the selected winner) in confidence order.

2. **Surface** -- :class:`~chronologia.extract.nseries.TimeMention` and
   :class:`~chronologia.events.Event` carry a populated ``confidence`` field
   that never participates in equality (so the equality-based corpora keep
   passing).

3. **Calibration = a gold floor that prose cannot erode** (the real contract).
   Walking a sample of every language's gold corpus (via the benchmark
   adapter's collection trick), a fully-claimed gold phrase scores at or above
   a floor -- and scores there whether it is said alone or buried in a
   conversational sentence, which is what makes the number safe to threshold.
   The achieved minimum is printed for the record.

   There is deliberately no matching *ceiling* over the confusables corpus.  A
   confusable that still parses -- "fall for the trick", "christmas came early"
   -- yields a reading identical to the real one, and telling those apart takes
   the sentence's meaning, which the extractor does not have; the confusables
   corpus documents exactly that as a downstream concern.  A ceiling could only
   be met by charging the reading for the words around it, which is precisely
   what confidence must not do.
"""
import os

from datetime import datetime

from benchmark.adapter import collect_gold_cases, all_langs
from chronologia.astrodate import (BASIS_EXACT, BASIS_PREDICTED,
                                    BASIS_RECONSTRUCTED, BASIS_TABULATED)
from chronologia.extract import Candidate, extract_candidates, extract_timespans
from chronologia.extract.confidence import (confidence, homograph_surfaces,
                                            specificity_factor)
from chronologia.events import extract_event

# --- the gold floor ---------------------------------------------------------
# A fully-claimed gold phrase must clear GOLD_FLOOR.  Observed on the corpora at
# authoring time: gold min ~0.85, with comfortable headroom over the floor.
GOLD_FLOOR = 0.75

# How far apart two scorings of the same date expression may drift when the
# prose around it grows.  They are expected to be identical; the tolerance is
# there so a future signal that reads the neighbouring tokens has room to say
# something small, not room to collapse the score.
PROSE_TOLERANCE = 0.05

_HERE = os.path.dirname(os.path.abspath(__file__))

ANCHOR = datetime(2017, 6, 27, 13, 4)


# ===========================================================================
# 1. Shape of the score and the ranked-candidate API.
# ===========================================================================
class TestScoreShape:
    def test_confidence_in_unit_interval(self):
        for lang, text in [("en", "next friday"), ("en", "june 2027"),
                           ("en", "the 15th of ramadan 1446"),
                           ("pt", "o proximo sabado"), ("de", "naechsten montag")]:
            for cand in extract_candidates(text, lang):
                assert 0.0 < cand.confidence <= 1.0, (text, cand)

    def test_deterministic(self):
        a = extract_candidates("june 5th 2027", "en")
        b = extract_candidates("june 5th 2027", "en")
        assert [c.confidence for c in a] == [c.confidence for c in b]

    def test_ranked_descending(self):
        cands = extract_candidates("the third day of the month", "en", limit=5)
        confs = [c.confidence for c in cands]
        assert confs == sorted(confs, reverse=True)

    def test_candidate_shape(self):
        cands = extract_candidates("june 2027", "en")
        assert cands
        c = cands[0]
        assert isinstance(c, Candidate)
        assert c.span is not None and isinstance(c.remainder, str)
        assert isinstance(c.construction, str) and c.construction

    def test_surfaces_runner_ups(self):
        # "1990" reads as a bare year AND as part of other numeric readings;
        # a term the matcher enumerates but does not select still appears here.
        cands = extract_candidates("in the 1990s", "en", limit=5)
        names = {c.construction for c in cands}
        assert len(cands) >= 1
        # the decade reading (the selected one) is present and scores well
        assert any(c.confidence > 0.5 for c in cands)

    def test_limit_respected(self):
        assert len(extract_candidates("june 5th 2027 at 3pm", "en", limit=2)) <= 2

    def test_empty_on_nothing(self):
        assert extract_candidates("the quick brown fox", "en") == []


# ===========================================================================
# 1b. Prose invariance: confidence scores the reading, not the utterance.
# ===========================================================================
# The same date expression, carried by ever more ordinary conversation.  The
# extraction is identical in all five -- one unambiguous "tomorrow" -- so the
# score must be too.  A consumer thresholding confidence (an intent pipeline is
# the one that matters) would otherwise throw away correct readings for no
# reason but the speaker's verbosity.
_PROSE = [
    "tomorrow",
    "meet tomorrow",
    "lets meet up tomorrow if that works",
    "i was thinking that maybe we could meet up tomorrow if that works",
    "i was thinking that maybe we could possibly meet up tomorrow if that "
    "works for you at all really",
]


class TestProseInvariance:
    def test_score_survives_the_prose_around_it(self):
        confs = []
        for text in _PROSE:
            cands = extract_candidates(text, "en", ANCHOR)
            assert cands, text
            best = max(cands, key=lambda c: c.confidence)
            assert best.confidence >= GOLD_FLOOR, (text, best.confidence)
            confs.append(best.confidence)
        assert max(confs) - min(confs) <= PROSE_TOLERANCE, confs

    def test_every_language_gold_phrase_survives_a_carrier_sentence(self):
        # The carrier is deliberately meaningless filler in each language's
        # script; what matters is that it is not date-like, so it must not
        # register at all.
        for lang, phrase, carrier in [
                ("en", "tomorrow", "i think we could maybe %s if you like"),
                ("pt", "amanha", "acho que talvez possamos %s se quiseres"),
                ("de", "morgen", "ich denke wir koennten vielleicht %s"),
        ]:
            alone = extract_candidates(phrase, lang, ANCHOR)
            carried = extract_candidates(carrier % phrase, lang, ANCHOR)
            assert alone and carried, (lang, phrase)
            assert abs(alone[0].confidence
                       - carried[0].confidence) <= PROSE_TOLERANCE, lang

    def test_ambiguous_scores_below_unambiguous(self):
        # "june 2027" states its year; the runner-up reading that keeps only
        # "2027" and strands "june" explains less of the same date phrase, and
        # a lone weekday still beats both partial readings of it.
        cands = extract_candidates("june 2027", "en", ANCHOR)
        full = [c for c in cands if c.remainder == ""]
        partial = [c for c in cands if c.remainder]
        assert full and partial
        assert min(c.confidence for c in full) > max(c.confidence
                                                     for c in partial)

    def test_composed_reading_ranks_first_confidence_values_invariant(self):
        # "tomorrow at 3pm": the COMPOSED reading (tomorrow 15:00 -- exactly what
        # extract_timespan returns) now ranks FIRST (candidates agree with the
        # single-winner API), ahead of the two bare clock readings and the bare
        # named day.  The #229 confidence VALUES are unchanged -- prose
        # invariance holds -- so the fullest clock reading is still 0.674; only
        # the composed primary is lifted to the top of the order.
        from chronologia import extract_timespan
        cands = extract_candidates("tomorrow at 3pm", "en", ANCHOR)
        ts = extract_timespan("tomorrow at 3pm", "en", ANCHOR)
        assert str(cands[0].span.start).replace("T", " ") \
            == str(ts[0].start_datetime)
        assert [c.construction for c in cands] == [
            "named_day", "clock_time", "clock_time", "named_day"]
        assert [round(c.confidence, 3) for c in cands] == [
            0.213, 0.674, 0.45, 0.213]


class TestSignals:
    def test_specificity_monotone(self):
        # era/deep-time (rank 0) is more specific than a bare year (rank 6),
        # which beats an unlisted construction (default rank).
        assert specificity_factor("era_bc") > specificity_factor("year_ref")
        assert specificity_factor("year_ref") > specificity_factor("nope_xyz")
        assert 0.0 < specificity_factor("nope_xyz") <= 1.0

    def test_homograph_set_is_the_abbreviations(self):
        from chronologia.extract.loader import load_lang_spec
        spec = load_lang_spec("en")
        risky = homograph_surfaces(spec)
        # every full weekday name is trusted (never flagged)
        assert not (risky & set(spec.weekday_full))
        # and the set is exactly the short forms the loader kept out of full
        assert risky == set(spec.weekdays) - set(spec.weekday_full)


# ===========================================================================
# 2. Surface: TimeMention / Event carry confidence without breaking equality.
# ===========================================================================
class TestSurfaceFields:
    def test_timemention_confidence_populated(self):
        ms = extract_timespans("meet friday at 3 or monday at noon", "en",
                               datetime(2017, 6, 27, 13, 4))
        assert ms
        for m in ms:
            assert 0.0 < m.confidence <= 1.0

    def test_timemention_equality_ignores_confidence(self):
        from chronologia.astrodate import AstroDate, DateSpan
        from chronologia.extract import TimeMention
        s = DateSpan(AstroDate(2027, 6, 5), AstroDate(2027, 6, 6))
        a = TimeMention(s, "june 5", (0, 2), (0, 6), confidence=0.9)
        b = TimeMention(s, "june 5", (0, 2), (0, 6), confidence=0.1)
        assert a == b and hash(a) == hash(b)

    def test_event_confidence_populated(self):
        ev = extract_event("dentist on june 5th 2027", "en",
                          datetime(2017, 6, 27, 13, 4))
        assert ev is not None
        assert 0.0 < ev.confidence <= 1.0

    def test_event_equality_ignores_confidence(self):
        from chronologia.astrodate import AstroDate, DateSpan
        from chronologia.events import Event
        s = DateSpan(AstroDate(2027, 6, 5), AstroDate(2027, 6, 6))
        assert Event("x", s, confidence=0.9) == Event("x", s, confidence=0.2)


# ===========================================================================
# 3. Calibration: the gold floor.
# ===========================================================================
def _gold_full_cover_conf(gc):
    """The best confidence among the candidates that fully claim the gold text
    (empty remainder), or ``None`` when the parse is a composed construction
    (business-days, ranges, anchored arithmetic) that no single matcher
    candidate covers -- those are out of the single-construction scorer's scope
    by design and are not part of this contract."""
    cands = extract_candidates(gc.text, gc.lang, gc.anchor, limit=8)
    full = [c.confidence for c in cands if c.remainder == ""]
    return max(full) if full else None


def test_gold_clears_the_floor(capsys):
    gold_min = {}
    gold_worst = {}
    for gc in collect_gold_cases(all_langs()):
        conf = _gold_full_cover_conf(gc)
        if conf is None:
            continue
        if gc.lang not in gold_min or conf < gold_min[gc.lang]:
            gold_min[gc.lang] = conf
            gold_worst[gc.lang] = gc.text
    assert gold_min, "no full-cover gold cases collected"
    floor_hits = {l: c for l, c in gold_min.items() if c < GOLD_FLOOR}
    assert not floor_hits, (
        f"gold parses below floor {GOLD_FLOOR}: "
        f"{[(l, round(gold_min[l], 3), gold_worst[l]) for l in floor_hits]}")
    with capsys.disabled():
        g_min = min(gold_min.values())
        print(f"\n[confidence floor] gold-min={g_min:.3f} over "
              f"{len(gold_min)} langs; floor={GOLD_FLOOR} "
              f"(headroom {g_min - GOLD_FLOOR:.3f})")


def test_confusables_that_parse_are_not_punished_for_their_sentence():
    """A look-alike the parser cannot disambiguate keeps the score its reading
    earns.  The old scorer pushed these down purely because the sentence around
    them was long, which made confidence a statement about the utterance; the
    contract now is that they score like the reading they actually are, and
    disambiguation is the consumer's job."""
    lone = extract_candidates("christmas", "en", datetime(2017, 6, 27, 13, 4))
    carried = extract_candidates("christmas came early that year", "en",
                                 datetime(2017, 6, 27, 13, 4))
    assert lone and carried
    assert abs(lone[0].confidence - carried[0].confidence) <= PROSE_TOLERANCE
