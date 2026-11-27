"""French "maintenant" and "tout de suite": the anchor instant.

Sources: TLFi (CNRTL) s.v. "maintenant", I.A: "À l'instant, au moment où l'on
dit «maintenant»"; TLFi s.v. "suite", 6.a: "Tout de suite [Dans le temps]
Aussitôt, sans délai."  Like en "now" and "right now", the word is read only
as the whole utterance, as a zero-width span at the anchor; inside a longer
phrase ("à partir de maintenant", "tout de suite après le dîner") it is not a
reading of its own.

Expected values are the anchor itself, by definition of the words.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse

A = datetime(2026, 11, 26, 10, 0)


@pytest.mark.parametrize("text", ["maintenant", "Maintenant",
                                  "tout de suite"])
def test_now_is_the_anchor(text):
    r = parse(text, A)
    assert r is not None, f"{text!r} did not parse"
    assert (r[0].start, r[0].end) == (ad(A), ad(A))
    assert r.remainder == ""


def test_now_inside_a_range_still_reads_as_an_endpoint():
    # "depuis lundi jusqu'à maintenant": from Monday 23 November to the anchor
    r = parse("depuis lundi jusqu'à maintenant", A)
    assert r is not None
    assert r[0].start == ad(datetime(2026, 11, 23))
    assert r[0].end == ad(A)
