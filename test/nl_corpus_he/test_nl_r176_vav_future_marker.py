# -*- coding: utf-8 -*-
"""R176: the curated vav-strip stems (``_HE_VAV_STEMS`` in
:mod:`chronologia.extract.numfold_semitic`) omitted בעוד (in/within,
``marker_future.voc``), the forward-direction sibling of the already-curated
לפני (before/ago). A vav-prefixed future offset ("ובעוד יומיים", and-in-
two-days) dropped the whole mention instead of resolving like its bare
sibling "בעוד יומיים".

Gold spans are computed by independent :mod:`datetime` arithmetic against the
shared ANCHOR (Tuesday 2017-06-27, 13:04), converted through ``ad()``.
"""
from datetime import timedelta

from ._corpus import ANCHOR, ad, start_end


def test_vav_future_bare_dual_day():
    offset_start = ANCHOR + timedelta(days=2)
    assert start_end("ובעוד יומיים") == (ad(offset_start),
                                          ad(offset_start + timedelta(days=1)))


def test_vav_future_bare_week():
    offset_start = ANCHOR + timedelta(weeks=1)
    assert start_end("ובעוד שבוע") == (ad(offset_start),
                                        ad(offset_start + timedelta(weeks=1)))


# --------------------------------------------------------------------------
# Controls: nothing the fix touches must regress.
# --------------------------------------------------------------------------
def test_control_bare_future_dual_day_unaffected():
    offset_start = ANCHOR + timedelta(days=2)
    assert start_end("בעוד יומיים") == (ad(offset_start),
                                         ad(offset_start + timedelta(days=1)))


def test_control_bare_future_week_unaffected():
    offset_start = ANCHOR + timedelta(weeks=1)
    assert start_end("בעוד שבוע") == (ad(offset_start),
                                       ad(offset_start + timedelta(weeks=1)))


def test_control_vav_before_unaffected():
    """Neighbouring #720/R172 stem (לפני) must be untouched."""
    offset_start = ANCHOR - timedelta(weeks=2)
    assert start_end("ולפני שבועיים") == (ad(offset_start),
                                           ad(offset_start + timedelta(weeks=1)))
