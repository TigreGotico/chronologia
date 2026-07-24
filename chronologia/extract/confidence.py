"""Deterministic confidence scoring for a resolved construction.

Every signal fed in here is *already computed* by the pipeline and would
otherwise be thrown away the moment the matcher picks a winner:

* **coverage of the date-bearing region** -- how much of the temporal material
  around it the construction actually claimed: its own token span over the
  width of the contiguous run of tokens some reading wanted
  (``match.length / extent``, see :func:`temporal_extent`).  A reading that
  leaves part of that run unexplained is the weaker of the readings competing
  over it; prose the parse walked past because it had nothing temporal to say
  is not part of the run and cannot lower anything.  This is what keeps
  confidence a statement about the *reading* rather than about the utterance --
  "tomorrow" is read exactly as confidently in a twenty-word sentence as it is
  alone;
* **construction specificity** -- derived straight from the compiler
  ``PRECEDENCE`` order (era/regnal/roman carry the most specific vocabulary and
  sit lowest; a bare ``year_ref`` is the least specific).  Lower rank == more
  specific == higher factor;
* **homograph risk** -- a bound surface drawn from the language's own
  weekday-abbreviation set (``weekdays`` minus the full names ``weekday_full``):
  the short forms that collide with common words ("mar", "so", "zo").  These are
  the documented-confusable surfaces the loader already separates out;
* **fold distance** -- a digit ("5") is trusted over a spelled number the
  ``numfold`` hook folded ("five") over a multiword surface the pipeline glued
  ("bronze age"); each rung down is a small penalty;
* **basis** -- the resolved :class:`~chronologia.astrodate.DateSpan`'s own
  provenance lattice: ``exact`` > ``tabulated`` > ``reconstructed`` >
  ``predicted``.

Combination -- a *weighted product*, not a sum or a learned model
------------------------------------------------------------------
``confidence = coverage * (spec^a * homograph^b * fold^c * basis^d)``

with ``a + b + c + d == 1``.  Coverage enters **linearly** (it is the dominant,
most discriminating signal: a reading that claims a quarter of what its rival
claims of the same text is a quarter as trustworthy) and the four quality
signals enter as a weighted
geometric mean bounded in ``(0, 1]``.  A product is chosen over a sum so that a
single collapsing signal (coverage -> 0) drags the whole score down the way a
weak link should, and because every factor is a unit-interval multiplier with a
clear "1.0 == no objection" reading.  The result lies in ``(0, 1]``,
monotone in every signal, and is fully deterministic -- there is **no** machine
learning here and the number is emphatically **not** a probability (see
``docs/extraction.md``).

The exponents ``a=0.40`` (spec), ``b=0.30`` (homograph), ``c=0.15`` (fold),
``d=0.15`` (basis) are a **declared ordering prior**, not a fitted model. They
were chosen, not learned: nothing in this file estimates them from data, and
no dataset backs them the way a regression coefficient would. They encode one
human judgement -- when two readings differ by exactly one defect apiece, a
specificity problem (the matcher picked a construction whose own vocabulary
argues it is the *wrong* reading) should discount trust more than a homograph
risk (a plausible reading leaning on an ambiguous short surface), which in
turn should discount more than a fold or basis wrinkle (the same fact stated
less directly, or dated by a coarser method) -- ``spec > homograph > fold ~
basis``. Swap in any other exponents that preserve that ranking and still sum
to 1 and the scorer's *behaviour* is unchanged in kind, only in degree; that
is the point of naming this a prior rather than a magic constant. The one
property this module guarantees mechanically -- proved in
``test/test_confidence_monotonicity.py``, not merely asserted here -- is
**monotonicity**: raising any single factor while holding the rest fixed never
lowers ``confidence``, and strictly raises it unless that factor is already
saturated at ``1.0``. The prior's *ordering* (that a specificity defect costs
more than a same-sized fold/basis defect) is also proved there as a concrete
inequality; calibration against real corpora (the separation between gold and
confusable scores) is a separate contract owned by ``test/test_confidence.py``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Iterator, Mapping, Optional

from chronologia.astrodate import (BASIS_EXACT, BASIS_PREDICTED,
                                    BASIS_RECONSTRUCTED, BASIS_TABULATED)
from chronologia.extract.compiler import PRECEDENCE
from chronologia.extract.model import LangSpec, Match, Resolution, Token

# --- specificity: a principled ordering read off the compiler precedence -----
# ``PRECEDENCE`` ranks constructions 0 (most specific: era/deep-time) upward;
# unlisted constructions default to 99.  We clamp the meaningful range to the
# rungs the table actually uses and map it linearly onto ``[_SPEC_FLOOR, 1.0]``
# so the most specific family scores 1.0 and the least specific never collapses
# the product on its own.
_RANK_CEIL = 12
_SPEC_FLOOR = 0.6

# --- basis: the resolved span's own provenance lattice ----------------------
_BASIS_FACTOR = {
    BASIS_EXACT: 1.0,
    BASIS_TABULATED: 0.9,
    BASIS_RECONSTRUCTED: 0.8,
    BASIS_PREDICTED: 0.7,
}

# --- fold distance: digit < spelled number < multiword ----------------------
_FOLD_SPELLED = 0.9
_FOLD_MULTIWORD = 0.85

# --- homograph: a bound short-form weekday surface ("mar", "so") -------------
_HOMOGRAPH_PENALTY = 0.6

# --- quality weights (must sum to 1.0) --------------------------------------
_W_SPEC = 0.40
_W_HOMOGRAPH = 0.30
_W_FOLD = 0.15
_W_BASIS = 0.15


def specificity_factor(construction: str) -> float:
    """Map a construction's compiler precedence to ``[_SPEC_FLOOR, 1.0]``."""
    rank = min(PRECEDENCE.get(construction, 99), _RANK_CEIL)
    return 1.0 - (1.0 - _SPEC_FLOOR) * (rank / _RANK_CEIL)


def homograph_surfaces(spec: LangSpec) -> frozenset:
    """The language's documented-confusable weekday surfaces.

    Exactly the abbreviation forms the loader kept out of ``weekday_full`` --
    the short weekday surfaces that also read as common words -- so a
    construction that leans on one is flagged homograph-risky with no
    hand-listed lexicon (the ambiguity data already lives in the locale)."""
    return frozenset(spec.weekdays) - frozenset(spec.weekday_full)


def _homograph_factor(slots: Mapping[str, Token], risky: frozenset) -> float:
    if any(tok.text in risky for tok in slots.values()):
        return _HOMOGRAPH_PENALTY
    return 1.0


def _fold_factor(tokens: Iterable[Token]) -> float:
    """Worst fold rung across the bound tokens: a multiword surface the
    pipeline glued (``" "`` in its text) outranks a spelled number the numfold
    hook produced (a number token whose raw carries no digit) outranks a plain
    digit run."""
    factor = 1.0
    for tok in tokens:
        if tok.text and " " in tok.text:
            factor = min(factor, _FOLD_MULTIWORD)
        elif tok.is_number and tok.raw and not any(c.isdigit() for c in tok.raw):
            factor = min(factor, _FOLD_SPELLED)
    return factor


def temporal_extent(matches: Iterable[Match]) -> Mapping[int, int]:
    """Width of the date-bearing region each match sits in, by match index.

    A reading answers for the temporal material around it, never for the
    sentence that happens to surround it.  The region is the contiguous run of
    tokens some reading claims -- matches that overlap or merely touch belong
    to the same run -- and it stops at the first token no reading wanted, which
    is exactly where the date-bearing material ends and the prose resumes.  So
    "at 3pm" in "tomorrow at 3pm" is measured against the whole four-token
    phrase it leaves partly unexplained, while "tomorrow" buried in twenty
    words of hedging is measured against itself alone: the hedging is not
    temporal material it failed to account for.
    """
    matches = list(matches)
    bounds = sorted((m.span for m in matches))
    regions = []
    for start, end in bounds:
        if regions and start <= regions[-1][1]:
            regions[-1][1] = max(regions[-1][1], end)
        else:
            regions.append([start, end])
    extents = {}
    for i, match in enumerate(matches):
        for start, end in regions:
            if start <= match.span[0] < end:
                extents[i] = end - start
                break
    return extents


def confidence(match: Match, resolution: Resolution, extent: int,
               spec: LangSpec) -> float:
    """Confidence in ``(0, 1]`` that ``match`` is the intended reading.

    This scores *how sure we are of the reading*, not how much of the utterance
    the reading accounts for.  Prose that is not date-like -- everything the
    parse walked past because it had nothing temporal to say -- leaves the
    score untouched, so "tomorrow" is read with the same confidence whether it
    stands alone or trails twenty words of conversational hedging.  What does
    lower the score is doubt about the reading itself: a rival reading of the
    same stretch of text claiming more of it (``extent``, the width of the
    date-bearing region from :func:`temporal_extent`), a construction whose own
    vocabulary is generic, a bound surface that collides with a common word, a
    fact stated indirectly, or a span dated by a coarser method.

    All signals are already-computed by-products of the parse; see the module
    docstring for the formula and its justification.  Deterministic, no ML, and
    **not** a probability -- a consumer may threshold it, but may not read it
    as "correct 85% of the time".
    """
    total = extent or 1
    coverage = min(max(match.length / total, 1e-6), 1.0)
    spec_f = specificity_factor(match.construction)
    homo_f = _homograph_factor(match.slots, homograph_surfaces(spec))
    fold_f = _fold_factor(match.slots.values())
    basis_f = _BASIS_FACTOR.get(resolution.value.basis, _BASIS_FACTOR[BASIS_PREDICTED])
    quality = (spec_f ** _W_SPEC * homo_f ** _W_HOMOGRAPH
               * fold_f ** _W_FOLD * basis_f ** _W_BASIS)
    return round(coverage * quality, 4)


@dataclass(frozen=True)
class ScoredCandidate:
    """One matcher reading carried through resolution and scored.

    This is the single structure every "scored reading" consumer shares.  It
    bundles the three views the pipeline used to derive at separate call sites:

    * ``match`` -- the enumerated :class:`~chronologia.extract.model.Match`
      (a construction, its token span, and its bound slots);
    * ``resolution`` -- what the resolver made of that reading against the
      anchor (a :class:`~chronologia.extract.model.Resolution`); readings the
      resolver rejects never become a ``ScoredCandidate`` at all;
    * ``confidence`` -- the deterministic score in ``(0, 1]`` from
      :func:`confidence`; **not** a probability.

    Note this is distinct from the *parse winner* the matcher's
    :meth:`~chronologia.extract.matcher.ConstructionMatcher._select` picks:
    that selection is resolution-independent (longest span, then compiler
    precedence) and runs before resolution is even attempted, because the
    winner contest must stand even for readings the resolver later declines.
    Confidence ranks *among resolved readings* for the candidate API; it does
    not choose the parse winner.  The two are different questions, and keeping
    them separate is deliberate -- see ``docs/extraction.md``.
    """

    match: Match
    resolution: Resolution
    confidence: float


def score_candidates(matches: Iterable[Match],
                     resolve: Callable[[Match], Optional[Resolution]],
                     spec: LangSpec) -> Iterator[ScoredCandidate]:
    """Resolve and score each reading -- the one place :func:`confidence` runs.

    ``matches`` are enumerated readings (either the whole candidate set from
    ``ConstructionMatcher._candidates`` for the ranked-candidate API, or the
    already-selected winners from ``ConstructionMatcher.match`` for per-mention
    scoring).  ``resolve`` maps a match to its resolution or ``None`` (the
    anchor is already bound by the caller).  Readings the resolver rejects are
    dropped; every survivor is yielded as a :class:`ScoredCandidate` carrying
    its single :func:`confidence` score.

    The readings are materialised before scoring because each one is scored
    against the date-bearing region it sits in (see :func:`temporal_extent`),
    which is a fact about the set and not about any single match.
    """
    matches = list(matches)
    extents = temporal_extent(matches)
    for i, match in enumerate(matches):
        res = resolve(match)
        if res is None:
            continue
        yield ScoredCandidate(match, res,
                              confidence(match, res, extents[i], spec))
