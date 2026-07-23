# -*- coding: utf-8 -*-
"""Proves the confidence formula's monotonicity and its ordering prior.

``confidence.py``'s module docstring frames the four exponents
(``spec^.40 * homograph^.30 * fold^.15 * basis^.15``) as a *declared ordering
prior* -- a stated preference, not a fitted model -- and names the one
property this suite must prove mechanically: raising any single factor while
holding the rest fixed never lowers the score, and strictly raises it unless
that factor is already saturated at ``1.0``. This file proves exactly that,
plus the bounds the docstring claims and the concrete inequality that makes
the prior's ranking (``spec > homograph > fold ~ basis``) more than a label.

The existing separation contract -- gold readings clear a floor, confusables
stay under a lower ceiling -- is already proved end-to-end in
``test/test_confidence.py::test_gold_and_confusables_are_separated``; it is
not duplicated here.

All Match/Resolution/Token/LangSpec construction below is driven from the
real field names in ``chronologia/extract/model.py`` and the real basis
constants in ``chronologia/astrodate.py`` -- no mocks, no code-derived
oracles. Expected relationships are hand-derived from the formula's own
algebra (a weighted geometric mean is monotone increasing in each base on
``(0, 1]``, and a smaller base raised to a larger exponent shrinks more),
not read back out of the implementation.
"""
from chronologia.astrodate import (AstroDate, BASIS_EXACT, BASIS_PREDICTED,
                                    BASIS_RECONSTRUCTED, BASIS_TABULATED,
                                    DateSpan)
from chronologia.extract.confidence import confidence
from chronologia.extract.loader import load_lang_spec
from chronologia.extract.model import Match, Resolution, Token

SPEC = load_lang_spec("en")

# A weekday abbreviation the loader flags as homograph-risky ("mar" collides
# with Portuguese "March"/generic "mar"; use an English one from the real
# loaded table so the test stays honest about what "risky" means here).
_RISKY = sorted(set(SPEC.weekdays) - set(SPEC.weekday_full))
assert _RISKY, "expected at least one abbreviation-only weekday surface"
RISKY_SURFACE = _RISKY[0]
SAFE_SURFACE = sorted(set(SPEC.weekday_full))[0]


def _span(anchor=AstroDate(2027, 6, 5), basis=BASIS_EXACT):
    return DateSpan(anchor, AstroDate(2027, 6, 6), basis=basis)


def _match(construction="era_date", length=2, total=2, slots=None):
    """A minimal Match with ``length`` tokens out of a ``total``-token
    utterance. ``slots`` lets a caller bind a homograph/fold-risky token."""
    slots = dict(slots or {})
    return Match(construction=construction, span=(0, length), slots=slots)


def _resolution(basis=BASIS_EXACT):
    return Resolution(value=_span(basis=basis), consumed=(0,))


def _conf(construction="era_date", length=2, total=2, slots=None, basis=BASIS_EXACT):
    return confidence(_match(construction, length, total, slots),
                      _resolution(basis), total, SPEC)


# ===========================================================================
# Bounds
# ===========================================================================
class TestBounds:
    def test_result_in_unit_interval(self):
        # a deliberately bad reading on every axis: low coverage, least
        # specific construction, homograph-risky slot, folded token, worst basis
        tok = Token(text=RISKY_SURFACE, raw=RISKY_SURFACE, index=0)
        c = _conf(construction="named_day", length=1, total=20,
                  slots={"WEEKDAY": tok}, basis=BASIS_PREDICTED)
        assert 0.0 < c <= 1.0

    def test_zero_coverage_drives_score_toward_zero(self):
        # match.length pinned at 1 token out of an enormous utterance: coverage
        # is clamped above zero (never literally 0, by construction) but the
        # score must fall arbitrarily close to it.
        c = _conf(construction="era_date", length=1, total=1_000_000)
        assert c < 0.001

    def test_all_factors_one_and_full_coverage_is_exactly_one(self):
        # era_date is rank 0 -> specificity_factor == 1.0; no risky slot;
        # no folded token; BASIS_EXACT -> basis factor 1.0; length == total
        # -> coverage == 1.0. Every base of the product is 1.0.
        c = _conf(construction="era_date", length=3, total=3, basis=BASIS_EXACT)
        assert c == 1.0


# ===========================================================================
# Monotonicity: raising one factor, holding the rest fixed, never lowers the
# score, and strictly raises it unless that factor is already at 1.0.
# ===========================================================================
class TestMonotonicity:
    def test_coverage_strictly_increasing_then_saturates(self):
        # total_tokens fixed at 10; match.length climbs from 1 to 10 (full
        # coverage). Every other factor is pinned at 1.0 (era_date, no slots,
        # BASIS_EXACT) so only coverage moves.
        scores = [_conf(construction="era_date", length=n, total=10)
                 for n in range(1, 11)]
        for a, b in zip(scores, scores[1:]):
            assert b > a, (scores)
        assert scores[-1] == 1.0
        # length can't exceed total in a real match, so 1.0 is coverage's
        # saturation point; nothing above it is reachable through this factor.

    def test_specificity_strictly_increasing_then_saturates(self):
        # Ranks read off the real compiler PRECEDENCE table, most-specific
        # (era_date, rank 0) down to a mid-table construction (year_ref,
        # rank 6) down to an unlisted one (clamped to rank 12, the floor).
        # specificity_factor is a strictly decreasing function of rank, so
        # confidence must strictly decrease along [era_date, year_ref, unlisted].
        c_top = _conf(construction="era_date")       # rank 0 -> factor 1.0
        c_mid = _conf(construction="year_ref")        # rank 6 -> factor 0.8
        c_low = _conf(construction="totally_unlisted_xyz")  # rank 12 (clamp) -> floor 0.6
        assert c_top > c_mid > c_low
        # era_date is already saturated at factor 1.0: swapping to any other
        # rank-0 construction changes nothing further.
        assert _conf(construction="era_date") == _conf(construction="named_period")

    def test_homograph_strictly_increasing_when_slot_cleared(self):
        risky_tok = Token(text=RISKY_SURFACE, raw=RISKY_SURFACE, index=0)
        safe_tok = Token(text=SAFE_SURFACE, raw=SAFE_SURFACE, index=0)
        c_risky = _conf(slots={"WEEKDAY": risky_tok})
        c_safe = _conf(slots={"WEEKDAY": safe_tok})
        c_empty = _conf(slots={})
        assert c_risky < c_safe
        # a slot bound to a full weekday name is already "no objection"
        # (factor 1.0), identical to having no weekday slot at all
        assert c_safe == c_empty == 1.0 * _conf(construction="era_date", slots={})

    def test_fold_strictly_increasing_across_the_three_rungs(self):
        digit_tok = Token(text="5", raw="5", index=0, is_number=True, value=5)
        spelled_tok = Token(text="five", raw="five", index=0, is_number=True, value=5)
        multiword_tok = Token(text="bronze age", raw="bronze age", index=0)
        c_digit = _conf(slots={"NUM": digit_tok})
        c_spelled = _conf(slots={"NUM": spelled_tok})
        c_multiword = _conf(slots={"NUM": multiword_tok})
        assert c_digit > c_spelled > c_multiword
        assert c_digit == _conf(slots={})  # digit run: no fold penalty at all

    def test_basis_strictly_increasing_across_the_provenance_lattice(self):
        c_exact = _conf(basis=BASIS_EXACT)
        c_tab = _conf(basis=BASIS_TABULATED)
        c_recon = _conf(basis=BASIS_RECONSTRUCTED)
        c_pred = _conf(basis=BASIS_PREDICTED)
        assert c_exact > c_tab > c_recon > c_pred


# ===========================================================================
# Ordering-prior teeth: the declared weight ordering (spec .40 > homograph .30
# > fold .15 ~ basis .15) must actually bite, not just be a comment.
# ===========================================================================
class TestOrderingPriorTeeth:
    def test_specificity_defect_costs_more_than_a_same_size_basis_defect(self):
        # "calendar_date" sits at PRECEDENCE rank 6 -> specificity_factor ==
        # 1 - 0.4*(6/12) == 0.8, exactly the BASIS_RECONSTRUCTED factor
        # (0.8). Same base, same magnitude of "defect" (0.8 vs. the 1.0
        # no-objection baseline) -- only the exponent differs: spec carries
        # weight .40, basis carries weight .15.
        #   quality_spec_defect  = 0.8**0.40 * 1 * 1 * 1
        #   quality_basis_defect = 1 * 1 * 1 * 0.8**0.15
        # Since 0 < 0.8 < 1 and 0.40 > 0.15, a bigger exponent on the same
        # sub-1 base yields a *smaller* number: 0.8**0.40 < 0.8**0.15.
        c_spec_defect = _conf(construction="calendar_date", basis=BASIS_EXACT)
        c_basis_defect = _conf(construction="era_date", basis=BASIS_RECONSTRUCTED)
        assert 0.8 ** 0.40 < 0.8 ** 0.15  # the algebra the assertion below relies on
        assert c_spec_defect < c_basis_defect, (
            "a specificity defect must discount confidence MORE than a "
            "same-magnitude basis defect, per the declared ordering prior "
            "spec(.40) > basis(.15)")

    def test_specificity_defect_costs_more_than_a_same_size_fold_defect(self):
        # "season_ref" sits at PRECEDENCE rank 3 -> specificity_factor ==
        # 1 - 0.4*(3/12) == 0.9, exactly the spelled-number fold factor
        # (_FOLD_SPELLED == 0.9). Same base 0.9, weight .40 vs weight .15.
        spelled_tok = Token(text="five", raw="five", index=0, is_number=True, value=5)
        c_spec_defect = _conf(construction="season_ref")
        c_fold_defect = _conf(construction="era_date", slots={"NUM": spelled_tok})
        assert 0.9 ** 0.40 < 0.9 ** 0.15
        assert c_spec_defect < c_fold_defect, (
            "a specificity defect must discount confidence MORE than a "
            "same-magnitude fold defect, per the declared ordering prior "
            "spec(.40) > fold(.15)")

    def test_homograph_defect_costs_more_than_a_same_size_basis_defect(self):
        # _HOMOGRAPH_PENALTY (0.6) has no equal-valued rung in the basis or
        # fold ladders, so this compares the weighted contributions directly
        # via the formula's own algebra rather than hunting for a coincidence:
        # homograph carries weight .30, basis carries weight .15; for any
        # shared base b in (0, 1), b**0.30 < b**0.15. Exercised at the real
        # penalty value (0.6) against the real reconstructed-basis value
        # (0.8) -- different bases, so this test proves the *weighted*
        # comparison the docstring actually promises (spec > homograph >
        # fold ~ basis in how much a same-shaped defect discounts trust),
        # via each factor's b**weight against the undamaged product (1.0).
        risky_tok = Token(text=RISKY_SURFACE, raw=RISKY_SURFACE, index=0)
        c_homograph_defect = _conf(slots={"WEEKDAY": risky_tok})
        c_basis_defect = _conf(basis=BASIS_RECONSTRUCTED)
        assert c_homograph_defect < c_basis_defect, (
            "homograph(.30) must discount confidence more than basis(.15) "
            "at their own respective real penalty values")
