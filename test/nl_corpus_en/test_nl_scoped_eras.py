"""Wave 1 -- scoped periods carrying an era marker ("the 3rd century bc").

A scoped period (century / millennium / decade) with a trailing BC/BCE marker
resolves on the BC axis; with an AD/CE marker it stays on the AD axis (the same
span the bare "the 3rd century" already gives, only with the marker consumed).

Span derivation (hand-checked, no engine output pinned).  The nth century BC is
the BC years ``(n-1)*100+1 .. n*100`` -- 1st century BC is 100..1 BC, 3rd is
300..201 BC.  In astronomical numbering X BC == year ``1 - X``, so:

* the OLDER edge (span start) is ``n*L`` BC == year ``1 - n*L``;
* the YOUNGER edge (span end, exclusive) is the first year of the next, more
  recent period, ``(n-1)*L`` BC == year ``1 - (n-1)*L``;

with ``L`` the period length in years (decade 10, century 100, millennium 1000).
So the 3rd century BC is ``[-299, -199)`` and the 1st millennium BC ``[-999, 1)``.
The width is one whole ``L`` of years -- a century-BC span reads CENTURY-wide.
"""
import pytest

from ._corpus import AstroDate, span, start_end, parse


# -- century BC (L=100): [1 - 100n, 1 - 100(n-1)) --------------------------

@pytest.mark.parametrize("text,n", [
    ("the 3rd century bc", 3), ("3rd century bce", 3),
    ("the 1st century bc", 1), ("the 5th century bc", 5),
    ("the 21st century bc", 21), ("2nd century bce", 2),
    ("the 4th century bce", 4),
])
def test_century_bc(text, n):
    s, e = start_end(text)
    assert s == AstroDate(1 - 100 * n, 1, 1)
    assert e == AstroDate(1 - 100 * (n - 1), 1, 1)
    assert span(text).width.days >= 100 * 365          # a century wide


# -- millennium / decade BC ------------------------------------------------

@pytest.mark.parametrize("text,n,L", [
    ("the 1st millennium bc", 1, 1000),
    ("the 2nd millennium bc", 2, 1000),
    ("the 3rd millennium bce", 3, 1000),
    ("the 2nd decade bc", 2, 10),
])
def test_millennium_decade_bc(text, n, L):
    s, e = start_end(text)
    assert s == AstroDate(1 - L * n, 1, 1)
    assert e == AstroDate(1 - L * (n - 1), 1, 1)


# -- explicit AD/CE stays on the AD axis (same span as the bare period) ----

@pytest.mark.parametrize("text,s,e", [
    ("2nd century ad", 100, 200), ("the 3rd century ad", 200, 300),
    ("the 21st century ce", 2000, 2100), ("the 1st millennium ad", 1, 1001),
])
def test_scoped_ad_axis(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s, 1, 1) and ee == AstroDate(e, 1, 1)


def test_ad_marker_leaves_no_remainder():
    # the era marker is consumed, not stranded in the remainder
    assert parse("the 2nd century ad")[1] == ""
    assert parse("the 3rd century bc")[1] == ""


# -- the bare scoped period is unchanged by the new BC/AD orders -----------

@pytest.mark.parametrize("text,s,e", [
    ("the 3rd century", 200, 300), ("the 21st century", 2000, 2100),
    ("the third millennium", 2000, 3000),
])
def test_bare_scoped_unchanged(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s, 1, 1) and ee == AstroDate(e, 1, 1)


# -- adversarial: the era reading requires the marker to TRAIL the period --

def _bc_century_span(n):
    return AstroDate(1 - 100 * n, 1, 1), AstroDate(1 - 100 * (n - 1), 1, 1)


@pytest.mark.parametrize("text", [
    "bc 3rd century",       # marker leads -> never the BC-century reading
    "the 3rd bc",           # no scope unit -> not a scoped-era period
    "the century bc",       # no ordinal
    "3rd bc century",       # marker between ord and unit
])
def test_not_a_scoped_bc(text):
    r = parse(text)
    if r is not None:
        assert (r[0].start, r[0].end) != _bc_century_span(3)
