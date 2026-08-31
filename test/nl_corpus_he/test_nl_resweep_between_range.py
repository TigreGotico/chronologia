# -*- coding: utf-8 -*-
"""Second-pass sweep: the ``בין X ו-Y`` ("between X and Y") range framing.

``marker_between.voc`` (בין) pairs with the ``ו`` coordinator per its own
documentation ("בין ינואר ומרץ" is cited there), but no test exercised the
construction end-to-end before this sweep.  All three endpoint granularities
are probed: bare month+year, and full day-level dates (same month, cross
month, cross year).  Gold is independent civil-calendar arithmetic, never the
parser.  The ``ו`` coordinator must be set off by a maqaf/hyphen
(``ו-<word>``) to tokenize as its own token; the fused literary form
(``ומרץ``, no hyphen) is a real, documented gap -- xfail'd below with the
correct gold, not asserted as passing.

The alternative closing marker ``ל-`` (cited as "standard" in Glinert §9.2
alongside the ו-coordinated form) is exercised too, both after a ``בין``
between-lead and after a ``מ-``/``מן`` from-lead: the dative-homograph
proclitic is licensed as a range terminal only when such a lead precedes it,
so a bare ``ל-<noun>`` dative is left untouched.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, nomatch, parse, start_end

_MONTHS = {
    1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל", 5: "מאי", 6: "יוני",
    7: "יולי", 8: "אוגוסט", 9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר",
    12: "דצמבר",
}
_MONTHS_B = {
    1: "בינואר", 2: "בפברואר", 3: "במרץ", 4: "באפריל", 5: "במאי",
    6: "ביוני", 7: "ביולי", 8: "באוגוסט", 9: "בספטמבר", 10: "באוקטובר",
    11: "בנובמבר", 12: "בדצמבר",
}


def _next_month(y, m):
    return (y + 1, 1) if m == 12 else (y, m + 1)


# -- bare year to year ------------------------------------------------------
@pytest.mark.parametrize("y1,y2", [
    (2015, 2018), (1990, 2000), (2001, 2001 + 1), (2020, 2030), (1948, 1967),
])
def test_between_year_range(y1, y2):
    text = f"בין {y1} ו-{y2}"
    ss, ee = start_end(text)
    assert ss == AstroDate(y1, 1, 1)
    assert ee == AstroDate(y2 + 1, 1, 1)


# -- month+year to month+year (same year and cross-year) --------------------
_MY_PAIRS = [
    (1, 2018, 4, 2018),
    (3, 2019, 8, 2019),
    (11, 2016, 2, 2017),
    (6, 2020, 6, 2021),
    (9, 2022, 12, 2022),
    (2, 2023, 1, 2024),
]


@pytest.mark.parametrize("m1,y1,m2,y2", _MY_PAIRS)
def test_between_month_year_range(m1, y1, m2, y2):
    text = f"בין {_MONTHS[m1]} {y1} ו-{_MONTHS[m2]} {y2}"
    ny, nm = _next_month(y2, m2)
    ss, ee = start_end(text)
    assert ss == AstroDate(y1, m1, 1)
    assert ee == AstroDate(ny, nm, 1)


# -- full day-level dates: same month, cross month, cross year --------------
_DAY_PAIRS = [
    (5, 1, 2018, 20, 1, 2018),     # same month
    (25, 3, 2019, 10, 4, 2019),    # cross month, same year
    (28, 12, 2019, 4, 1, 2020),    # cross year
    (1, 6, 2021, 30, 6, 2021),     # same month, full span
    (15, 7, 2024, 3, 8, 2024),     # cross month
]


@pytest.mark.parametrize("d1,m1,y1,d2,m2,y2", _DAY_PAIRS)
def test_between_full_date_range(d1, m1, y1, d2, m2, y2):
    text = f"בין {d1} {_MONTHS_B[m1]} {y1} ו-{d2} {_MONTHS_B[m2]} {y2}"
    s = date(y1, m1, d1)
    e = date(y2, m2, d2) + timedelta(days=1)
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)


# -- fused ו- (no hyphen): the literary form ("ומרץ") used to be swallowed,
# collapsing the range to just its first endpoint.  A range-only pre_hook
# (``split_he_range_word``, chronologia/extract/numfold_semitic.py) now
# splits a vav-glued month/weekday/daypart word off before range detection
# reads the pretoken stream, so the second endpoint is visible again.
def test_between_fused_and_pending():
    ss, ee = start_end("בין ינואר ומרץ")
    assert ss == AstroDate(2017, 1, 1)
    assert ee == AstroDate(2017, 4, 1)


# -- ל- as the "between" closing marker binds the 2nd endpoint ---------------
# marker_to.voc's prose (and Glinert §9.2) call "בין ... ל..." standard
# alongside the ו-coordinated form.  The proclitic ל־ ("to") is a dative
# homograph, so it is licensed as a range terminal only after a from-lead
# (מ־/מן) or a between-lead (בין) -- the same lead-required guard the Romance
# directional "a" uses.  A between-lead is present here, so all three
# granularities bind their second endpoint.
def test_between_lamed_month():
    ss, ee = start_end("בין ינואר ל-אפריל")
    assert ss == AstroDate(2017, 1, 1)
    assert ee == AstroDate(2017, 5, 1)


def test_between_lamed_year():
    ss, ee = start_end("בין 2015 ל-2018")
    assert ss == AstroDate(2015, 1, 1)
    assert ee == AstroDate(2019, 1, 1)


def test_between_lamed_full_date():
    ss, ee = start_end("בין 15 בינואר 2020 ל-20 בינואר 2020")
    assert ss == AstroDate(2020, 1, 15)
    assert ee == AstroDate(2020, 1, 21)


# -- מ-X ל-Y : the "from X to Y" framing with the ל- terminal ----------------
# The canonical Hebrew temporal range is "מ... עד..." (from ... until ...); the
# proclitic ל־ terminal ("מ־ינואר ל־אפריל") is the equally common colloquial
# variant.  The from-lead (מ־/מן) licenses ל־ as a range terminal.  RTL: the
# earlier date reads first and is the start; end is exclusive (day after the
# last day, first day of the month after the last month, Jan 1 of the year
# after the last year).  Gold is independent civil-calendar arithmetic.
@pytest.mark.parametrize("y1,y2", [
    (2015, 2018), (1990, 2000), (2001, 2002), (2020, 2030), (1948, 1967),
])
def test_from_lamed_year_range(y1, y2):
    ss, ee = start_end(f"מ-{y1} ל-{y2}")
    assert ss == AstroDate(y1, 1, 1)
    assert ee == AstroDate(y2 + 1, 1, 1)


@pytest.mark.parametrize("m1,y1,m2,y2", _MY_PAIRS)
def test_from_lamed_month_year_range(m1, y1, m2, y2):
    text = f"מ-{_MONTHS[m1]} {y1} ל-{_MONTHS[m2]} {y2}"
    ny, nm = _next_month(y2, m2)
    ss, ee = start_end(text)
    assert ss == AstroDate(y1, m1, 1)
    assert ee == AstroDate(ny, nm, 1)


@pytest.mark.parametrize("d1,m1,y1,d2,m2,y2", _DAY_PAIRS)
def test_from_lamed_full_date_range(d1, m1, y1, d2, m2, y2):
    text = f"מ-{d1} {_MONTHS_B[m1]} {y1} ל-{d2} {_MONTHS_B[m2]} {y2}"
    s = date(y1, m1, d1)
    e = date(y2, m2, d2) + timedelta(days=1)
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)


# -- the מן free-form from-lead licenses ל- just as the proclitic מ- does -----
def test_from_lamed_year_range_min_leadform():
    ss, ee = start_end("מן 2015 ל-2018")
    assert ss == AstroDate(2015, 1, 1)
    assert ee == AstroDate(2019, 1, 1)


# -- guard: bare ל- with NO from/between lead is the dative, never a range ----
# "ל-3 שעות" ("for 3 hours"), "נסעתי ל-2020" ("I drove to[wards] 2020") carry
# no from/between lead, so the ל- terminal must not fire and fabricate a range.
def test_bare_lamed_dative_is_not_a_range():
    nomatch("ל-3 שעות")


def test_bare_lamed_no_lead_single_year_untouched():
    # a lone year after a bare dative ל- resolves to that year as a single
    # span; the ל- must NOT turn it into a range with a fabricated second end.
    r = parse("נסעתי ל-2020")
    if r is not None:
        s = r[0]
        assert s.start == AstroDate(2020, 1, 1)
        assert s.end == AstroDate(2021, 1, 1)
