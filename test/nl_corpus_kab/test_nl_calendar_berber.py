# -*- coding: utf-8 -*-
"""Berber (Amazigh) calendar dates in Kabyle.

kab already uses the Berber month names as the *Gregorian* civil-month
vocabulary (see ``test_nl_calendar.py``), so the only unambiguous surface
the ``berber`` calendar can bind here is a bare 4-digit year read against
``calendar_year_range`` (2900-3060) in ``lang.json``'s ``year_ref``
construction. A ``MONTH DAY? YEAR?`` phrase such as "yennayer 2976" is
grammatically identical to an ordinary Gregorian calendar_date and
``nongregorian_date`` outranks it, so wiring a ``CAL_MONTH`` construction
here would silently break every existing Gregorian month+year reading
(verified and rejected -- see the refusal-pin test below); only the bare
year is bound.

Gold values are hand-derived from ``julian_to_jdn``/``jdn_to_gregorian``
under the +950 era shift, independent of the ``berber`` calendar's own
``to_jdn``/``from_jdn`` (see ``test/test_calendars.py``)."""
from datetime import date
import pytest
from ._corpus import ANCHOR, AstroDate, start, start_end


@pytest.mark.parametrize("text,gy", [("2976", 2026), ("2975", 2025),
                                     ("2978", 2028), ("3000", 2050),
                                     ("2900", 1950)])
def test_bare_year_in_berber_range_resolves_via_berber_calendar(text, gy):
    # 1 Yennayer of berber year Y == Gregorian (Y - 950)-01-14; the bare
    # year_ref span covers the whole berber year, so it starts there.
    s, e = start_end(text)
    assert s == AstroDate(gy, 1, 14)
    assert e == AstroDate(gy + 1, 1, 14)


@pytest.mark.parametrize("text,gy", [(str(y), y) for y in
                                     (1999, 2020, 1969, 1830, 2899, 3061)])
def test_bare_year_outside_berber_range_stays_gregorian(text, gy):
    # just below/above the 2900-3060 window: an ordinary Gregorian year.
    s, e = start_end(text)
    assert s == AstroDate(gy, 1, 1)
    assert e == AstroDate(gy + 1, 1, 1)


def test_yennayer_2976_month_year_phrase_reads_as_literal_gregorian():
    # REFUSAL-PIN: no CAL_MONTH construction is wired for kab (see module
    # docstring), so "yennayer 2976" resolves through the ordinary
    # calendar_date construction -- 2976 read as a literal (proleptic)
    # Gregorian year, NOT as a berber-calendar date. This is the current,
    # deliberately limited behaviour, not the berber new year.
    s = start("yennayer 2976")
    assert s == AstroDate(2976, 1, 1)


def test_day_month_year_still_gregorian_for_low_years():
    # control: ordinary Gregorian month+day+year readings outside the
    # berber year range are unaffected by the year_ref calendar binding.
    assert start("3 yennayer 2027") == AstroDate(2027, 1, 3)
