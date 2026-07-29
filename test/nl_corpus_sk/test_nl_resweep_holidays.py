# -*- coding: utf-8 -*-
"""Second-pass sweep: Slovak holiday references with an explicit year, fresh
years.

test_nl_holiday_ref.py covers the bare next-occurrence form plus two spot
checks with an explicit year ("veľká noc 2020", "nový rok 2020"); this file
sweeps every lexically-recognised sk holiday (chronologia/holiday_data/i18n/
well_known.tab) across 20 fresh years each, none of which repeat the two
years already pinned there. Fixed feasts are plain calendar dates; the
Easter-cycle feasts (veľká noc, kvetná nedeľa, veľký piatok, veľkonočný
pondelok, fašiangy) are derived from an INDEPENDENT Western computus
(``dateutil.easter.easter``), never the parser: kvetná nedeľa = Easter-7
(Palm Sunday), veľký piatok = Easter-2 (Good Friday), veľkonočný pondelok =
Easter+1 (Easter Monday), fašiangy = Easter-47 (Shrove Tuesday, the last day
of carnival before Ash Wednesday). "čínsky nový rok" (Chinese New Year) is
left out: its date needs a lunisolar calendar this corpus has no independent
oracle for, so pinning years to it would risk an unverifiable gold."""
from datetime import timedelta

import pytest
from dateutil.easter import easter

from ._corpus import AstroDate, start

_YEARS = [1998, 2001, 2003, 2006, 2009, 2011, 2013, 2014, 2016, 2017,
          2019, 2022, 2026, 2028, 2029, 2031, 2032, 2033, 2036, 2040]

_FIXED = {
    "nový rok": (1, 1),
    "vianoce": (12, 25),
    "štedrý deň": (12, 24),
    "traja králi": (1, 6),
    "sviatok všetkých svätých": (11, 1),
    "halloween": (10, 31),
    "valentín": (2, 14),
}

_EASTER_OFFSET = {
    "veľká noc": 0,
    "kvetná nedeľa": -7,
    "veľký piatok": -2,
    "veľkonočný pondelok": 1,
    "fašiangy": -47,
}

_FIXED_CASES = [(f"{name} {y}", (y, m, d))
                 for name, (m, d) in _FIXED.items() for y in _YEARS]

_EASTER_CASES = [(f"{name} {y}", (easter(y) + timedelta(days=off)))
                   for name, off in _EASTER_OFFSET.items() for y in _YEARS]


@pytest.mark.parametrize("text,ymd", _FIXED_CASES)
def test_fixed_holiday_fresh_year(text, ymd):
    assert start(text) == AstroDate(*ymd), text


@pytest.mark.parametrize("text,d", _EASTER_CASES)
def test_easter_cycle_holiday_fresh_year(text, d):
    assert start(text) == AstroDate(d.year, d.month, d.day), text
