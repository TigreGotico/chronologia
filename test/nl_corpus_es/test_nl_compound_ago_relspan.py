# -*- coding: utf-8 -*-
"""Spanish equivalents of ``test/nl_corpus_en/test_nl_compound_ago_relspan.py``
-- defect R109.

Spanish carries a POSTPOSED "ago" marker ("atrás", direction -1) alongside
the preposed "hace", so the same leading-chunk-folding gap applies: "3 meses
y 2 dias atrás" only applied "2 dias atrás", stranding "3 meses y". Spanish
also has ``rel_span`` ("2 próximas semanas" == "the next 2 weeks"), so the
trailing-chunk-extends-the-span fix applies too.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, parse, start_end

LANG = "es"


def _point(anchor=ANCHOR, **delta):
    dt = anchor + relativedelta(**delta)
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


@pytest.mark.parametrize("text", [
    "3 meses y 2 dias atrás",
    "2 dias y 3 meses atrás",           # reversed textual order: same instant
])
def test_ago_compound_folds_leading_chunk(text):
    span_, remainder = parse(text)
    exp_start = _point(months=-3, days=-2)
    assert span_.start == exp_start, f"{text!r}: {span_.start} != {exp_start}"
    assert span_.end == exp_start + timedelta(days=1)
    assert remainder == "", f"{text!r} left a remainder: {remainder!r}"


def test_ago_bare_control_unchanged():
    span_, remainder = parse("hace 3 meses")
    exp_start = _point(months=-3)
    assert span_.start == exp_start
    assert span_.end == _point(months=-2)
    assert remainder == ""


def test_rel_span_next_extends_forward():
    start, end = start_end("2 próximas semanas y 3 dias")
    today = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    assert start == _ad(today)
    assert end == _ad(today + timedelta(weeks=2, days=3))


def test_rel_span_bare_control_unchanged():
    start, end = start_end("2 próximas semanas")
    today = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    assert start == _ad(today)
    assert end == _ad(today + timedelta(weeks=2))
