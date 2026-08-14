# -*- coding: utf-8 -*-
"""ru relative_offset symmetry between the forward "через X" ("in X") and
backward "X назад" ("X ago") directions.

Two independent invariants, both carried by ``relative_offset.orders``:

1. The 1.5-quantifier ("полтора"/"полторы", ``spec.quantifiers["1.5"]``)
   works for durations (see test_nl_r170_pol_compound.py) because
   ``extract_duration`` reads QUANT directly; the offset grammar binds it
   through its own ``QUANT UNIT MARKER`` / ``MARKER QUANT UNIT`` orders.
   Unlike "полчаса" -- folded to a numeric token ("0.5") by the number-fold
   hook *before* grammar matching, so it rides the ``NUM``-based orders --
   "полтора" is not fold-eligible and reaches the grammar as a QUANT token.
2. ``MARKER USG`` (bare unit + marker, implied qty 1) covers forward
   offsets ("через час") and ``USG MARKER`` mirrors it for backward ones
   ("час назад"/"неделю назад"/"день назад").

Every span below is one calendar/clock unit wide, starting at its own
directional endpoint (not the anchor) -- exactly the convention the existing
"через час" -> [11:00, 12:00) case already sets: a "назад" span still runs
[t, t+unit) with t the qty-units-back point, not [anchor-unit, anchor).
Anchor: Fri 2026-08-14 10:00. All gold spans hand-computed.
"""
from datetime import datetime

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

LANG = "ru"
ANCHOR = datetime(2026, 8, 14, 10, 0)


def span(text):
    r = extract_timespan(text, LANG, ANCHOR)
    assert r is not None, f"{text!r} did not resolve"
    return r[0].start, r[0].end


def _dt(*args):
    return AstroDate(*args)


# -- defect 1: полтора/полторы (1.5) on the offset path --------------------

def test_poltora_chasa_forward():
    assert span("через полтора часа") == (
        _dt(2026, 8, 14, 11, 30), _dt(2026, 8, 14, 12, 30))


def test_poltora_chasa_backward():
    assert span("полтора часа назад") == (
        _dt(2026, 8, 14, 8, 30), _dt(2026, 8, 14, 9, 30))


# -- defect 2: bare-unit "назад" mirrors bare-unit "через" ------------------

def test_bare_chas_forward_control():
    # already worked before this fix (MARKER USG); kept as a control.
    assert span("через час") == (
        _dt(2026, 8, 14, 11, 0), _dt(2026, 8, 14, 12, 0))


def test_bare_chas_backward():
    assert span("час назад") == (
        _dt(2026, 8, 14, 9, 0), _dt(2026, 8, 14, 10, 0))


def test_bare_den_forward_control():
    assert span("через день") == (
        _dt(2026, 8, 15, 10, 0), _dt(2026, 8, 16, 10, 0))


def test_bare_den_backward():
    assert span("день назад") == (
        _dt(2026, 8, 13, 10, 0), _dt(2026, 8, 14, 10, 0))


def test_bare_nedelya_forward_control():
    assert span("через неделю") == (
        _dt(2026, 8, 21, 10, 0), _dt(2026, 8, 28, 10, 0))


def test_bare_nedelya_backward():
    assert span("неделю назад") == (
        _dt(2026, 8, 7, 10, 0), _dt(2026, 8, 14, 10, 0))


# -- controls that must not regress -----------------------------------------

def test_control_poluchasa_forward_unaffected():
    # "полчаса" number-folds to a NUM token ("0.5") before grammar matching,
    # so it always rode the pre-existing "MARKER NUM UNIT" order.
    assert span("через полчаса") == (
        _dt(2026, 8, 14, 10, 30), _dt(2026, 8, 14, 11, 30))


def test_control_3_chasa_backward_unaffected():
    assert span("3 часа назад") == (
        _dt(2026, 8, 14, 7, 0), _dt(2026, 8, 14, 8, 0))


def test_control_bare_chas_no_marker_still_unresolved():
    # the pinned no-marker-disambiguation decision (see
    # test_nl_r170_pol_compound.py::test_bare_chas_not_supported for the
    # duration-side twin) must survive: without через/назад, "час" alone
    # collides with the clock idiom "в час" and stays unresolved.
    assert extract_timespan("час", LANG, ANCHOR) is None


def test_not_an_offset_control():
    assert extract_timespan("тут нет времени", LANG, ANCHOR) is None
