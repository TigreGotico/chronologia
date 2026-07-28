# -*- coding: utf-8 -*-
"""Day-period bands (cs) on deictic days: ráno=04-12, odpoledne=12-18, večer=18-22 (CLDR cs day-period bands), anchored to the named day. Bands already asserted in test_nl_daypart.py are excluded to avoid duplication."""
import pytest
from datetime import timedelta
from ._corpus import AstroDate, start_end


CASES = [
    ('dnes odpoledne', (2017, 6, 27, 12), (2017, 6, 27, 18)),
    ('dnes večer', (2017, 6, 27, 18), (2017, 6, 27, 22)),
    ('včera ráno', (2017, 6, 26, 4), (2017, 6, 26, 12)),
    ('včera odpoledne', (2017, 6, 26, 12), (2017, 6, 26, 18)),
    ('zítra ráno', (2017, 6, 28, 4), (2017, 6, 28, 12)),
    ('zítra večer', (2017, 6, 28, 18), (2017, 6, 28, 22)),
    ('odpoledne', (2017, 6, 27, 12), (2017, 6, 27, 18)),
    ('večer', (2017, 6, 27, 18), (2017, 6, 27, 22)),
]


@pytest.mark.parametrize("text,s,e", CASES)
def test_span(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))
