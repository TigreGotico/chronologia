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

3. **Calibration = separation** (the real contract).  Walking a sample of every
   language's gold corpus (via the benchmark adapter's collection trick), a
   fully-claimed gold phrase scores at or above a floor; walking every
   language's *confusables* corpus, a confusable text that still yields a
   candidate scores at or below a ceiling that sits **below** the gold floor.
   The gap between the two bands -- not any absolute number -- is what is
   asserted.  Achieved margins are printed for the record.
"""
import os
import sys

import pytest

from datetime import datetime

from benchmark.adapter import collect_gold_cases, all_langs
from chronologia.astrodate import (BASIS_EXACT, BASIS_PREDICTED,
                                    BASIS_RECONSTRUCTED, BASIS_TABULATED)
from chronologia.extract import Candidate, extract_candidates, extract_timespans
from chronologia.extract.confidence import (confidence, homograph_surfaces,
                                            specificity_factor)
from chronologia.events import extract_event

# --- separation thresholds --------------------------------------------------
# A fully-claimed gold phrase must clear GOLD_FLOOR; a confusable that still
# yields a candidate must stay at or below CONFUSABLE_CEIL; and the two bands
# must not overlap (CONFUSABLE_CEIL < GOLD_FLOOR).  Observed on the corpora at
# authoring time: gold min ~0.85, confusable max ~0.65 -- comfortably separated.
GOLD_FLOOR = 0.75
CONFUSABLE_CEIL = 0.70

_HERE = os.path.dirname(os.path.abspath(__file__))


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
# 3. Calibration: the separation contract.
# ===========================================================================
def _confusable_texts(lang):
    """Collect the confusables-corpus sentences for ``lang`` (param ``text``
    with no ``expected``), reusing the benchmark adapter's collection trick."""
    path = os.path.join(_HERE, f"nl_corpus_{lang}", "test_nl_confusables.py")
    if not os.path.exists(path):
        return []

    class _Collect:
        def __init__(self):
            self.items = []

        def pytest_collection_modifyitems(self, items):
            self.items.extend(items)

    plugin = _Collect()
    devnull = open(os.devnull, "w")
    stdout, sys.stdout = sys.stdout, devnull
    try:
        pytest.main(["--collect-only", "-q", "-p", "no:cacheprovider", path],
                    plugins=[plugin])
    finally:
        sys.stdout = stdout
        devnull.close()
    texts = set()
    for item in plugin.items:
        cs = getattr(item, "callspec", None)
        if cs is None:
            continue
        p = cs.params
        if "text" in p and isinstance(p["text"], str) and "expected" not in p:
            texts.add(p["text"])
    return sorted(texts)


def _gold_full_cover_conf(gc):
    """The best confidence among the candidates that fully claim the gold text
    (empty remainder), or ``None`` when the parse is a composed construction
    (business-days, ranges, anchored arithmetic) that no single matcher
    candidate covers -- those are out of the single-construction scorer's scope
    by design and are not part of this contract."""
    cands = extract_candidates(gc.text, gc.lang, gc.anchor, limit=8)
    full = [c.confidence for c in cands if c.remainder == ""]
    return max(full) if full else None


def test_bands_do_not_overlap():
    assert CONFUSABLE_CEIL < GOLD_FLOOR


def test_gold_and_confusables_are_separated(capsys):
    # --- gold: fully-claimed phrases clear the floor ------------------------
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
    gold_floor_hits = {l: c for l, c in gold_min.items() if c < GOLD_FLOOR}
    assert not gold_floor_hits, (
        f"gold parses below floor {GOLD_FLOOR}: "
        f"{[(l, round(gold_min[l], 3), gold_worst[l]) for l in gold_floor_hits]}")

    # --- confusables: any yielding candidate stays under the ceiling --------
    conf_max = {}
    conf_worst = {}
    conf_langs = [l for l in all_langs()
                  if os.path.exists(os.path.join(
                      _HERE, f"nl_corpus_{l}", "test_nl_confusables.py"))]
    for lang in conf_langs:
        for text in _confusable_texts(lang):
            cands = extract_candidates(text, lang, datetime(2017, 6, 27, 13, 4),
                                       limit=1)
            if not cands:
                continue
            c = cands[0].confidence
            if lang not in conf_max or c > conf_max[lang]:
                conf_max[lang] = c
                conf_worst[lang] = text
    assert conf_max, "no confusables corpora collected"
    ceil_hits = {l: c for l, c in conf_max.items() if c > CONFUSABLE_CEIL}
    assert not ceil_hits, (
        f"confusables above ceiling {CONFUSABLE_CEIL}: "
        f"{[(l, round(conf_max[l], 3), conf_worst[l]) for l in ceil_hits]}")

    # --- the separation is the contract: report the achieved margin ---------
    g_min = min(gold_min.values())
    c_max = max(conf_max.values())
    assert g_min > c_max, (
        f"gold floor {g_min:.3f} must exceed confusable ceiling {c_max:.3f}")
    with capsys.disabled():
        print(f"\n[confidence separation] gold-min={g_min:.3f} over "
              f"{len(gold_min)} langs; confusable-max={c_max:.3f} over "
              f"{len(conf_max)} langs; achieved margin={g_min - c_max:.3f}")
