# -*- coding: utf-8 -*-
"""All three attested Kabyle 'weekend' surfaces resolve to the coming Fri-Sat.

special_weekend.voc lists taggara n ssmana / taggara n dduṛt / taggara n
yimalas ("end of the week"), all attested by native speaker athmanemokraoui
(#265); weekend_start=Friday (lang.json). From Tue anchor 2017-06-27 the coming
weekend is Fri 2017-06-30 -> Sun 2017-07-02 (two days wide).
"""
import pytest

from ._corpus import span

_SURFACES = [
    "taggara n ssmana",
    "taggara n dduṛt",
    "taggara n yimalas",
]


@pytest.mark.parametrize("text", _SURFACES)
def test_weekend_friday_saturday(text):
    s = span(text)
    assert s.start_datetime.date().isoformat() == "2017-06-30"  # Friday
    assert (s.end_datetime - s.start_datetime).days == 2
