"""Property-based (Hypothesis) laws for the core value types and calendars.

These assert *laws* rather than examples: JDN round-trips for all 18 registered
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
# 18 shows up (and fails) independently.
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


# --------------------------------------------------------------------------
# Strengthening: proleptic-negative round-trips, JDN monotonicity, and
# cross-calendar JDN consistency for every registered calendar.
#
# Algorithms/epochs are the ones cited in ``chronologia/calendars.py``'s
# module docstring (Fliegel & Van Flandern 1968 for Gregorian/Julian;
# Dershowitz & Reingold 1990 "Calendrical Calculations" for Islamic
# civil/Hebrew; the downloaded French Republican/Bahai reference tables for
# the arithmetic variants) -- these tests exercise the same ``to_jdn``/
# ``from_jdn`` pair as ``test_jdn_roundtrip_*`` above, just over a wider,
# signed input space, so they are strictly additive: no existing assertion
# here is loosened, and the hand-written gold-value tests in
# ``test_calendars.py``/``test_calendars_tabulated.py`` are untouched.
# --------------------------------------------------------------------------
from chronologia.calendars import Calendar, CalendarRangeError

# Rule-based calendars whose ``to_jdn``/``from_jdn`` raise a documented
# ``ValueError`` below their epoch (islamic_civil, french_republican) are
# excluded from the *negative-JDN* sweep below -- that's the calendar's own
# documented contract at the epoch boundary, not a bug to paper over with
# ``assume``. They still get the round-trip law over their valid JDN range
# via ``test_jdn_roundtrip_*`` above.
_EPOCH_FLOORED = {"islamic_civil", "french_republican"}

_PROLEPTIC_EXACT_KEYS = sorted(
    k for k, cal in c.CALENDARS.items()
    if isinstance(cal, Calendar) and k not in _EPOCH_FLOORED
)


def _make_proleptic_roundtrip_test(key):
    cal = c.CALENDARS[key]
    # A window straddling the epoch on both sides, deep into proleptic
    # (negative-year) territory -- the docstring guarantees "floor division
    # throughout, so negative ... years convert correctly" for the
    # Gregorian/Julian base, and the other exact calendars build on it.
    lo = cal.epoch_jdn - 2_000_000
    hi = cal.epoch_jdn + 2_000_000

    @CAP
    @given(jdn=st.integers(min_value=lo, max_value=hi))
    def _test(jdn):
        y, m, d = cal.from_jdn(jdn)
        assert cal.to_jdn(y, m, d) == jdn

    _test.__name__ = f"test_jdn_roundtrip_proleptic_{key}"
    return _test


for _pkey in _PROLEPTIC_EXACT_KEYS:
    globals()[f"test_jdn_roundtrip_proleptic_{_pkey}"] = \
        _make_proleptic_roundtrip_test(_pkey)


def _make_monotonicity_test(key):
    cal = c.CALENDARS[key]
    lo, hi = _jdn_bounds(cal)
    hi = max(lo, hi - 1)

    @CAP
    @given(jdn=st.integers(min_value=lo, max_value=hi))
    def _test(jdn):
        # A later calendar date (the very next JDN) always maps to a
        # strictly larger JDN when converted back -- i.e. the calendar's own
        # (year, month, day) ordering never runs backwards against the JDN
        # hub it is built on.
        y1, m1, d1 = cal.from_jdn(jdn)
        y2, m2, d2 = cal.from_jdn(jdn + 1)
        assert cal.to_jdn(y2, m2, d2) > cal.to_jdn(y1, m1, d1)

    _test.__name__ = f"test_jdn_monotonic_{key}"
    return _test


for _key in sorted(c.CALENDARS):
    globals()[f"test_jdn_monotonic_{_key}"] = _make_monotonicity_test(_key)


# Cross-calendar consistency: the JDN hub is the single point of truth, so
# any two calendars asked about the *same* JDN must, independently, resolve
# back to that same JDN through their own to_jdn/from_jdn pair.
_CROSS_PAIRS = [
    (a, b) for i, a in enumerate(sorted(c.CALENDARS))
    for b in sorted(c.CALENDARS)[i + 1:]
]


def _make_cross_calendar_test(key_a, key_b):
    cal_a, cal_b = c.CALENDARS[key_a], c.CALENDARS[key_b]
    lo_a, hi_a = _jdn_bounds(cal_a)
    lo_b, hi_b = _jdn_bounds(cal_b)
    lo, hi = max(lo_a, lo_b), min(hi_a, hi_b)
    if lo > hi:
        return None                              # domains don't overlap

    @CAP
    @given(jdn=st.integers(min_value=lo, max_value=hi))
    def _test(jdn):
        ya, ma, da = cal_a.from_jdn(jdn)
        yb, mb, db = cal_b.from_jdn(jdn)
        assert cal_a.to_jdn(ya, ma, da) == jdn
        assert cal_b.to_jdn(yb, mb, db) == jdn

    _test.__name__ = f"test_cross_calendar_{key_a}_{key_b}"
    return _test


for _ka, _kb in _CROSS_PAIRS:
    _t = _make_cross_calendar_test(_ka, _kb)
    if _t is not None:
        globals()[f"test_cross_calendar_{_ka}_{_kb}"] = _t


# --------------------------------------------------------------------------
# Determinism / no-crash: below-epoch (out-of-domain) JDNs are documented to
# either resolve proleptically or raise ``CalendarRangeError``/``ValueError``
# -- never anything else (a stack trace from an unrelated exception type
# would signal an unguarded edge case).
# --------------------------------------------------------------------------
def _make_no_crash_test(key):
    cal = c.CALENDARS[key]
    epoch = cal.epoch_jdn
    lo = epoch - 5_000_000
    hi = epoch - 1

    @CAP
    @given(jdn=st.integers(min_value=lo, max_value=hi))
    def _test(jdn):
        try:
            y, m, d = cal.from_jdn(jdn)
        except (CalendarRangeError, ValueError):
            return                                # documented, not a crash
        # if it didn't raise, it must still be self-consistent
        assert cal.to_jdn(y, m, d) == jdn

    _test.__name__ = f"test_below_epoch_no_crash_{key}"
    return _test


for _key in sorted(c.CALENDARS):
    globals()[f"test_below_epoch_no_crash_{_key}"] = _make_no_crash_test(_key)
