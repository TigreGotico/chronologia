"""Hungarian "fél óra múlva": a fraction of a unit counted from now.

"fél" is a half and "negyed" a quarter (en.wiktionary, s.v. fél, numeral
sense), so "fél óra múlva" is 30 minutes after the 13:04 anchor, 13:34, and
"negyed óra múlva" is 13:19.  "fél órával ezelőtt" is 30 minutes before,
12:34.  The quantifier is part of the offset, so it does not stay in the
remainder.
"""
import pytest

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text,hour,minute", [
    ("fél óra múlva", 13, 34),
    ("negyed óra múlva", 13, 19),
    ("fél órával ezelőtt", 12, 34),
])
def test_fraction_of_an_hour(text, hour, minute):
    r = parse(text)
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(hour=hour, minute=minute))
    assert r.remainder == ""
