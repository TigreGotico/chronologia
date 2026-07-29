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

The alternative closing marker ``ל-`` (also cited as "standard" in
``marker_to.voc``'s prose) is probed too and found to silently drop the
second endpoint at every granularity (month, year, and full date) -- a
systematic bug, xfail'd with correct gold rather than swept as if it worked.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

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


# -- known gap: fused ו- (no hyphen) drops the second endpoint --------------
@pytest.mark.xfail(reason="the ו coordinator must be set off by a maqaf/hyphen "
                          "(ו-מרץ) to tokenize separately; the fused literary "
                          "form (ומרץ) is swallowed and the range collapses to "
                          "just the first endpoint month instead of matching "
                          "Jan-Mar or failing to match at all",
                   strict=True)
def test_between_fused_and_pending():
    ss, ee = start_end("בין ינואר ומרץ")
    assert ss == AstroDate(2017, 1, 1)
    assert ee == AstroDate(2017, 4, 1)


# -- known gap: ל- as the "between" closing marker drops the 2nd endpoint ---
@pytest.mark.xfail(reason="marker_to.voc's own prose calls 'בין ... ל...' "
                          "standard alongside the ו-coordinated form, but the "
                          "engine only wires marker_and (ו) to marker_between, "
                          "not marker_to (עד/ל); 'ל-<endpoint>' after בין is "
                          "silently dropped and the range collapses to a "
                          "single day/month/year at the first endpoint",
                   strict=True)
def test_between_lamed_month_pending():
    ss, ee = start_end("בין ינואר ל-אפריל")
    assert ss == AstroDate(2017, 1, 1)
    assert ee == AstroDate(2017, 5, 1)


@pytest.mark.xfail(reason="same ל- closing-marker gap as "
                          "test_between_lamed_month_pending, at the bare-year "
                          "granularity",
                   strict=True)
def test_between_lamed_year_pending():
    ss, ee = start_end("בין 2015 ל-2018")
    assert ss == AstroDate(2015, 1, 1)
    assert ee == AstroDate(2019, 1, 1)


@pytest.mark.xfail(reason="same ל- closing-marker gap as "
                          "test_between_lamed_month_pending, at the full "
                          "day-level date granularity",
                   strict=True)
def test_between_lamed_full_date_pending():
    ss, ee = start_end("בין 15 בינואר 2020 ל-20 בינואר 2020")
    assert ss == AstroDate(2020, 1, 15)
    assert ee == AstroDate(2020, 1, 21)
