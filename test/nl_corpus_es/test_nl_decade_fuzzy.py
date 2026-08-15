# -*- coding: utf-8 -*-
"""early/mid/late composed with the Spanish decade construction (es):
"a principios/mediados/finales de los años NNNN" and the word-form decade
"los años noventa" -- same snap-to-year thirds convention as
month_fuzzy/decade_ref's German sibling ("Anfang der 2000er"), hand-derived
independently of the parser (see ``_third_snap`` below)."""
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import parse, start_end


def _snap_year(dt):
    lo = datetime(dt.year, 1, 1)
    hi = datetime(dt.year + 1, 1, 1)
    return lo if (dt - lo) <= (hi - dt) else hi


def _third_snap(s, e, part):
    """Independent re-derivation of decade_ref's snap="year" thirds: cut at
    total_days * idx // 3 from the decade start, then round the interior cut
    to the nearest January 1st (the span endpoints stay exact)."""
    total_days = (e - s).days
    idx = {"early": 0, "mid": 1, "late": 2}[part]

    def cut(i):
        return _snap_year(s + timedelta(days=total_days * i // 3))

    a = s if idx == 0 else cut(idx)
    b = e if idx == 2 else cut(idx + 1)
    return AstroDate.from_datetime(a), AstroDate.from_datetime(b)


DECADE_2000S = (datetime(2000, 1, 1), datetime(2010, 1, 1))
DECADE_90S = (datetime(1990, 1, 1), datetime(2000, 1, 1))

_CASES = [
    ('a principios de los años 2000', DECADE_2000S, 'early'),
    ('a mediados de los años 2000', DECADE_2000S, 'mid'),
    ('a finales de los años 2000', DECADE_2000S, 'late'),
    ('a principios de los años noventa', DECADE_90S, 'early'),
    ('a mediados de los años noventa', DECADE_90S, 'mid'),
    ('a finales de los años noventa', DECADE_90S, 'late'),
]


@pytest.mark.parametrize("text,decade,part", _CASES)
def test_decade_fuzzy(text, decade, part):
    want_s, want_e = _third_snap(*decade, part)
    s, e = start_end(text)
    assert s == want_s
    assert e == want_e


def test_bare_decade_still_whole_span():
    # regression: the bare decade (no fuzzy PART) must keep matching the
    # WHOLE ten-year span with no stranded remainder.
    s, e = start_end('los años 2000')
    assert s == AstroDate(2000, 1, 1)
    assert e == AstroDate(2010, 1, 1)
    assert parse('los años 2000')[1] == ""


def test_bare_decade_word_form_still_whole_span():
    s, e = start_end('los años noventa')
    assert s == AstroDate(1990, 1, 1)
    assert e == AstroDate(2000, 1, 1)
    assert parse('los años noventa')[1] == ""


@pytest.mark.xfail(strict=True, reason=(
    "pre-existing, separate defect: 'a principios de <plain GYEAR>' binds "
    "the bare YEAR construction (whole year) instead of composing PART with "
    "the year, stranding 'a principios de' in the remainder. Correct gold "
    "would be the early third of the year, 2000-01-01..2000-05-02T16:00 "
    "(exact elapsed-microsecond thirds -- a single year does not snap to "
    "year like a decade/century does). Not touched by the decade_ref "
    "fuzzy-composition fix this file covers."))
def test_plain_year_fuzzy_prefix_not_yet_composed():
    want_s = AstroDate(2000, 1, 1)
    want_e = AstroDate.from_datetime(
        datetime(2000, 1, 1) + (datetime(2001, 1, 1) - datetime(2000, 1, 1)) / 3)
    s, e = start_end('a principios de 2000')
    assert s == want_s
    assert e == want_e
    assert parse('a principios de 2000')[1] == ""
