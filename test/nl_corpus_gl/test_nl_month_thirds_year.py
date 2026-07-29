# -*- coding: utf-8 -*-
"""gl month-thirds with an explicit TRAILING year: "early/mid/late <month>
<year>" must place the third inside the NAMED year, not the anchor's own.

Regression pin for the systemic Romance/Uralic silent-wrong where a trailing
explicit year was ignored (the third resolved in the anchor year and the year
was stranded as unread residue).  The equal-thirds boundaries are computed here
by independent date arithmetic -- the parser is never consulted for the oracle.
"""
from datetime import datetime, timedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, ad, start_end


def _thirds(year, month):
    """(early, mid, late) as (start, end) AstroDate pairs -- equal thirds of the
    Gregorian month, independently of the parser."""
    first = datetime(year, month, 1)
    nxt = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    third = (nxt - first) / 3
    b1, b2 = first + third, first + 2 * third
    return {
        "early": (ad(first), ad(b1)),
        "mid": (ad(b1), ad(b2)),
        "late": (ad(b2), ad(nxt)),
    }


_G = _thirds(2019, 3)


def test_early_month_third_binds_explicit_year():
    assert start_end("a principios de marzo de 2019") == _G["early"]


def test_mid_month_third_binds_explicit_year():
    assert start_end("a mediados de marzo de 2019") == _G["mid"]


def test_late_month_third_binds_explicit_year():
    assert start_end("a finais de marzo de 2019") == _G["late"]


def test_yearless_month_third_stays_anchor_year_regression():
    # WITHOUT a year the third stays in the anchor's own year (2017) -- pinned
    # byte-identical so the explicit-year fix does not perturb the yearless path.
    early = _thirds(ANCHOR.year, 3)["early"]
    assert start_end("a principios de marzo") == early
