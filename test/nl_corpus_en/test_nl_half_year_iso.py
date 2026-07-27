"""ISO / financial half-year designators: "H1 2020", "2020 H1", "H2 2021".

``H1``/``H2`` are the ISO-8601-extension / business surface for the very same
semantics the spelled "the first/second half of 2020" already resolves through
the ``half_period`` construction: H1 is January 1 .. July 1, H2 is July 1 ..
the following January 1.  They must therefore resolve to the identical span as
the spelled form -- one construction, one resolver, two surfaces.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import ANCHOR, start_end, parse


@pytest.mark.parametrize("text,s,e", [
    ("H1 2020", (2020, 1, 1), (2020, 7, 1)),
    ("H2 2020", (2020, 7, 1), (2021, 1, 1)),
    ("H1 2021", (2021, 1, 1), (2021, 7, 1)),
    ("H2 2021", (2021, 7, 1), (2022, 1, 1)),
    ("2020 H1", (2020, 1, 1), (2020, 7, 1)),
    ("2021 H2", (2021, 7, 1), (2022, 1, 1)),
])
def test_iso_half_year(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


def test_h1_reads_as_the_spelled_half_does():
    """H1/H2 are only a surface for the same calendar half, so they must
    resolve to the identical span as the spelled "first/second half of"."""
    assert start_end("H1 2020") == start_end("the first half of 2020")
    assert start_end("H2 2020") == start_end("the second half of 2020")


def test_iso_half_year_lowercase():
    """The designator is case-insensitive input; "h1 2020" is "H1 2020"."""
    assert start_end("h1 2020") == (AstroDate(2020, 1, 1), AstroDate(2020, 7, 1))


def test_h1_inside_a_sentence():
    s, e = start_end("revenue grew in H1 2020")
    assert (s, e) == (AstroDate(2020, 1, 1), AstroDate(2020, 7, 1))


@pytest.mark.parametrize("text", ["H3 2020", "H0 2020", "H9 2020"])
def test_a_number_that_names_no_half_is_not_a_half(text):
    """Only H1 and H2 name a calendar half; anything else does not fire the
    half construction (it must not resolve to a clean Jan-Jul / Jul-Jan span)."""
    r = parse(text)
    if r is not None:
        s, e = r[0].start, r[0].end
        is_half = (s.day == 1 and e.day == 1
                   and ((s.month, e.month) == (1, 7)
                        or (s.month == 7 and e.year == s.year + 1
                            and e.month == 1)))
        assert not is_half
