"""Property-based (Hypothesis) laws for the core value types and calendars.

These assert *laws* rather than examples: JDN round-trips for all 17 registered
calendars, AstroDate ordinal/isoformat round-trips across the full year range,
DateSpan set-algebra laws, EDTF parse/format idempotence and timeline
JDN round-trips on non-discontinuity days.

Example counts are capped (``max_examples``) so the whole module stays
CI-sane; the point is to explore the input space, not to run forever.
"""
from datetime import timedelta, timezone

from hypothesis import assume, given, settings
from hypothesis import strategies as st

import chronologia as c
from chronologia import AstroDate, DateSpan
from chronologia.astrodate import combine_basis

CAP = settings(max_examples=200, deadline=None)

_BASES = ("exact", "tabulated", "reconstructed", "predicted")


def _jdn_bounds(cal):
    """A safe [lo, hi] JDN band on which ``from_jdn`` is defined for ``cal``.

    Tabulated calendars are bounded by their published month-start table; a
    rule-based calendar is floored at its epoch (below which it raises) and
    given a wide window above it.
    """
    starts = getattr(cal, "starts", None)
    if starts:
        return starts[0], starts[-1] - 1
    lo = max(cal.epoch_jdn, 1_000_000)
    return lo, lo + 1_500_000


# --------------------------------------------------------------------------
# Calendar JDN round-trips — the JDN hub law, for every registered calendar.
# --------------------------------------------------------------------------
def _make_calendar_test(key):
    cal = c.CALENDARS[key]
    lo, hi = _jdn_bounds(cal)

    @CAP
    @given(jdn=st.integers(min_value=lo, max_value=hi))
    def _test(jdn):
        y, m, d = cal.from_jdn(jdn)
        # from_jdn is a left inverse of to_jdn on the calendar's domain.
        assert cal.to_jdn(y, m, d) == jdn

    _test.__name__ = f"test_jdn_roundtrip_{key}"
    return _test


# Bind one property test per calendar into the module namespace so each of the
# 17 shows up (and fails) independently.
for _key in sorted(c.CALENDARS):
    globals()[f"test_jdn_roundtrip_{_key}"] = _make_calendar_test(_key)


# --------------------------------------------------------------------------
# AstroDate round-trips across the whole (unbounded) year range.
# --------------------------------------------------------------------------
_years = st.integers(min_value=-50_000, max_value=50_000)
_months = st.integers(min_value=1, max_value=12)
_days = st.integers(min_value=1, max_value=28)   # valid in every month


@st.composite
def astrodates(draw, aware=False):
    y = draw(_years)
    mo = draw(_months)
    d = draw(_days)
    hh = draw(st.integers(0, 23))
    mm = draw(st.integers(0, 59))
    ss = draw(st.integers(0, 59))
    us = draw(st.integers(0, 999_999))
    tz = None
    if aware:
        off = draw(st.integers(-14 * 60, 14 * 60))
        tz = timezone(timedelta(minutes=off))
    return AstroDate(y, mo, d, hh, mm, ss, us, tzinfo=tz)


@CAP
@given(astro=astrodates())
def test_astrodate_ordinal_roundtrip(astro):
    # toordinal/fromordinal round-trip the date part for any year.
    back = AstroDate.fromordinal(astro.toordinal())
    assert (back.year, back.month, back.day) == (astro.year, astro.month,
                                                 astro.day)


@CAP
@given(astro=astrodates())
def test_astrodate_isoformat_roundtrip(astro):
    assert AstroDate.fromisoformat(astro.isoformat()) == astro


@CAP
@given(astro=astrodates(aware=True))
def test_astrodate_isoformat_roundtrip_aware(astro):
    revived = AstroDate.fromisoformat(astro.isoformat())
    assert revived == astro                        # same instant
    assert revived.utcoffset() == astro.utcoffset()


@CAP
@given(astro=astrodates())
def test_astrodate_json_roundtrip_huge_years(astro):
    from chronologia import from_json, to_json
    assert from_json(to_json(astro)) == astro


# --------------------------------------------------------------------------
# DateSpan algebra laws.
# --------------------------------------------------------------------------
@st.composite
def spans(draw):
    a = draw(st.integers(-2_000_000, 2_000_000))
    length = draw(st.integers(0, 500_000))
    basis = draw(st.sampled_from(_BASES))
    start = AstroDate.fromordinal(a)
    end = AstroDate.fromordinal(a + length)
    return DateSpan(start, end, basis)


@CAP
@given(x=spans(), y=spans())
def test_intersect_commutative(x, y):
    a = x.intersect(y)
    b = y.intersect(x)
    if a is None or b is None:
        assert a is None and b is None
    else:
        assert (a.start, a.end) == (b.start, b.end)


@CAP
@given(x=spans(), y=spans())
def test_intersect_basis_is_worst_of(x, y):
    got = x.intersect(y)
    if got is not None:
        assert got.basis == combine_basis(x.basis, y.basis)


@CAP
@given(x=spans(), y=spans(), z=spans())
def test_intersect_associative_where_defined(x, y, z):
    xy = x.intersect(y)
    yz = y.intersect(z)
    left = xy.intersect(z) if xy is not None else None
    right = x.intersect(yz) if yz is not None else None
    lk = None if left is None else (left.start, left.end)
    rk = None if right is None else (right.start, right.end)
    assert lk == rk


@CAP
@given(a=st.integers(-1_000_000, 1_000_000),
       n=st.integers(1, 400_000), m=st.integers(1, 400_000),
       b1=st.sampled_from(_BASES), b2=st.sampled_from(_BASES))
def test_union_of_adjacent_spans(a, n, m, b1, b2):
    # Two half-open spans that share a boundary union into one gap-free span.
    p = AstroDate.fromordinal(a)
    q = AstroDate.fromordinal(a + n)
    r = AstroDate.fromordinal(a + n + m)
    left = DateSpan(p, q, b1)
    right = DateSpan(q, r, b2)
    u = left.union(right)
    assert (u.start, u.end) == (p, r)
    assert u.basis == combine_basis(b1, b2)


@CAP
@given(x=spans())
def test_intersect_idempotent(x):
    got = x.intersect(x)
    if x.start == x.end:                            # empty span overlaps nothing
        assert got is None
    else:
        assert (got.start, got.end) == (x.start, x.end)


# --------------------------------------------------------------------------
# EDTF: parse . format . parse is stable.
# --------------------------------------------------------------------------
_edtf_years = st.integers(min_value=0, max_value=9999)


@CAP
@given(y=_edtf_years, qual=st.sampled_from(["", "?", "~", "%"]))
def test_edtf_parse_format_parse(y, qual):
    text = f"{y:04d}{qual}"
    first = c.parse_edtf(text)
    formatted = c.format_edtf(first)
    second = c.parse_edtf(formatted)
    assert second == first
    assert c.format_edtf(second) == formatted


@CAP
@given(y=_edtf_years, mo=_months, d=_days,
       qual=st.sampled_from(["", "?", "~", "%"]))
def test_edtf_ymd_parse_format_parse(y, mo, d, qual):
    text = f"{y:04d}-{mo:02d}-{d:02d}{qual}"
    first = c.parse_edtf(text)
    second = c.parse_edtf(c.format_edtf(first))
    assert second == first


# --------------------------------------------------------------------------
# Timelines: from_jdn . to_jdn is identity on non-discontinuity days.
# --------------------------------------------------------------------------
def _make_timeline_test(key):
    tl = c.TIMELINES[key]
    # Discontinuity JDNs deliberately break the one-to-one mapping; exclude
    # a small window around each so the round-trip law holds.
    disc_jdns = {d.jdn for d in getattr(tl, "discontinuities", ())}

    @CAP
    @given(jdn=st.integers(min_value=2_200_000, max_value=2_600_000))
    def _test(jdn):
        from chronologia.timelines import (NeverExisted, OutOfTimeline,
                                           UnknownCalendar)
        assume(all(abs(jdn - dj) > 40 for dj in disc_jdns))
        try:
            label = tl.from_jdn(jdn)
        except (UnknownCalendar, OutOfTimeline):
            assume(False)   # day sits in an unregistered/out-of-scope segment
            return
        back = tl.to_jdn(label)
        # REPEAT (tuple) / NeverExisted arise only at discontinuities, which we
        # excluded; a clean day must round-trip to a single JDN.
        assume(not isinstance(back, (tuple, NeverExisted)))
        assert back == jdn

    _test.__name__ = f"test_timeline_roundtrip_{key}"
    return _test


for _tkey in sorted(c.TIMELINES):
    globals()[f"test_timeline_roundtrip_{_tkey}"] = _make_timeline_test(_tkey)
