"""A connector is the longest of its surfaces that starts at a token.

German "bis" and "bis zum" are both surfaces of "until"; "bis zum montag"
takes the two-word surface.  A dotted era marker is compared on the tokens
the tokenizer gives, without the dots: "v. chr." and "v.chr." are the two
tokens "v" and "chr".
"""
import pytest

from chronologia.extract.loader import load_lang_spec
from chronologia.extract.matcher import _connector_span
from chronologia.extract.pipeline import pretokens


@pytest.mark.parametrize("text, name, at, consumed", [
    ("bis zum montag", "until", 0, 2),
    ("bis montag", "until", 0, 1),
    ("montag bis", "until", 0, 0),
    ("500 v. chr.", "bc", 1, 2),
    ("500 v.chr.", "bc", 1, 2),
    ("500 vor christus", "bc", 1, 2),
    ("500 vor christi geburt", "bc", 1, 3),
])
def test_the_longest_surface_is_the_connector(text, name, at, consumed):
    spec = load_lang_spec("de")
    tokens = pretokens(text, spec)
    assert _connector_span(name, tokens, at, spec) == consumed
