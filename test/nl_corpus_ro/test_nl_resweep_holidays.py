# -*- coding: utf-8 -*-
"""Second-pass Romanian named-holiday sweep, fresh years.

Anchor 2017-06-27 (a Tuesday, 13:04). Each fixed civil holiday from
``test_nl_national_holidays_2.py`` is exercised again here with an explicit
year suffix, over 20 years that file never uses (2010-2016, 2022-2025,
2027-2029, 2031-2036), so no (text, gold) pair is duplicated.

Movable feasts (Paște / Crăciun / Vinerea Mare) were probed against the live
parser and are NOT recognised as holiday keywords at all -- "crăciun 2016"
degrades to a bare-year parse and "vinerea mare 2017" degrades to a bare
"vinerea" (next Friday) match, ignoring "mare" and the year. Per policy on
uncertain idioms with no library-code fix in scope, they are dropped from
this corpus rather than xfailed.

Each fixed date is hand-verified against the same official sources cited in
``chronologia/civil_holidays/well_known.py``.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, span, start

_FRESH_YEARS = (
    2010, 2011, 2012, 2013, 2014, 2015, 2016,
    2022, 2023, 2024, 2025,
    2027, 2028, 2029,
    2031, 2032, 2033, 2034, 2035, 2036,
)

_TEMPLATES = [
    ("anul nou {y}", (1, 1)),
    ("unirea principatelor {y}", (1, 24)),
    ("ziua unirii principatelor române {y}", (1, 24)),
    ("mica unire {y}", (1, 24)),
    ("ziua muncii {y}", (5, 1)),
    ("ziua copilului {y}", (6, 1)),
    ("ziua internațională a copilului {y}", (6, 1)),
    ("ziua națională {y}", (12, 1)),
    ("ziua națională a româniei {y}", (12, 1)),
    ("ziua marii uniri {y}", (12, 1)),
    ("adormirea maicii domnului {y}", (8, 15)),
    ("sfânta maria mare {y}", (8, 15)),
]


def _cases():
    out = []
    for y in _FRESH_YEARS:
        for tmpl, (m, d) in _TEMPLATES:
            out.append((tmpl.format(y=y), (y, m, d)))
    return out


@pytest.mark.parametrize("text,ymd", _cases())
def test_holiday_explicit_year_resweep(text, ymd):
    assert start(text) == AstroDate(*ymd), text
    assert span(text).width == timedelta(days=1)
