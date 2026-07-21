# -*- coding: utf-8 -*-
"""Assert every parity pair yields the SAME span in this language as in en."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR
from .parity import PARITY


@pytest.mark.parametrize("loc,en", PARITY)
def test_parity_same_span_as_en(loc, en):
    a = extract_timespan(loc, "es", ANCHOR)
    b = extract_timespan(en, "en", ANCHOR)
    assert a is not None, f"{{loc!r}} did not parse in es"
    assert b is not None, f"{{en!r}} did not parse in en"
    assert a[0].start == b[0].start, f"start mismatch {{loc!r}} vs {{en!r}}"
    assert a[0].end == b[0].end, f"end mismatch {{loc!r}} vs {{en!r}}"
