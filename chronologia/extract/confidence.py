"""Deterministic confidence scoring for a resolved construction.

Every signal fed in here is *already computed* by the pipeline and would
otherwise be thrown away the moment the matcher picks a winner:

* **token coverage** -- how much of the utterance the construction actually
  consumed (``match.length / total_tokens``).  A whole phrase that binds every
  token ("next friday") is trusted; a single homograph token stranded in a
  six-word sentence ("*may* the force be with you") is not;
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
most discriminating signal: a fragment that covers a quarter of the text is a
quarter as trustworthy) and the four quality signals enter as a weighted
geometric mean bounded in ``(0, 1]``.  A product is chosen over a sum so that a
single collapsing signal (coverage -> 0) drags the whole score down the way a
weak link should, and because every factor is a unit-interval multiplier with a
clear "1.0 == no objection" reading.  The result lies in ``(0, 1]``,
monotone in every signal, and is fully deterministic -- there is **no** machine
learning here and the number is emphatically **not** a probability (see
``docs/extraction.md``).
"""
from __future__ import annotations

from typing import Iterable, Mapping

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


def confidence(match: Match, resolution: Resolution, total_tokens: int,
               spec: LangSpec) -> float:
    """Confidence in ``(0, 1]`` that ``match`` is the intended reading.

    All signals are already-computed by-products of the parse; see the module
    docstring for the formula and its justification.  Deterministic, no ML, and
    **not** a probability.
    """
    total = total_tokens or 1
    coverage = min(max(match.length / total, 1e-6), 1.0)
    spec_f = specificity_factor(match.construction)
    homo_f = _homograph_factor(match.slots, homograph_surfaces(spec))
    fold_f = _fold_factor(match.slots.values())
    basis_f = _BASIS_FACTOR.get(resolution.value.basis, _BASIS_FACTOR[BASIS_PREDICTED])
    quality = (spec_f ** _W_SPEC * homo_f ** _W_HOMOGRAPH
               * fold_f ** _W_FOLD * basis_f ** _W_BASIS)
    return round(coverage * quality, 4)
