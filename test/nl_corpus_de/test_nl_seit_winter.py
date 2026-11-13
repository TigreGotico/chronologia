# -*- coding: utf-8 -*-
""""seit dem Winter" opens at the most recent winter start.

chronologia reads the meteorological winter, 1 December to 1 March
(``chronologia/edtf.py``).  The winter that holds 1 January 2025 started on
1 December 2024; the most recent winter start before 1 March 2026 and before
20 June 2026 is 1 December 2025.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse


@pytest.mark.parametrize("text", ["seit dem winter", "seit winter"])
@pytest.mark.parametrize("anchor", [datetime(2026, 3, 1, 12, 0),
                                    datetime(2026, 6, 20, 12, 0)])
def test_seit_winter_is_the_last_winter(text, anchor):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(datetime(2025, 12, 1)),
                                          ad(anchor))
    assert r.remainder == ""
