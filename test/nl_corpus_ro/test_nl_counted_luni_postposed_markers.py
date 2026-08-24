"""ro -- "luni" is both Monday and the plural of "lună" (month), so a COUNT
before it names months, never Mondays.  The canonical past phrasing puts the
marker first ("acum 2 luni"), but the marker can also trail the count or be a
"<from> <present>" pair, and those shapes must reach the same verdict: the
homographic surface never yields a counted-weekday reading whichever side the
marker sits on.

Where the months reading is expressible the phrase resolves as months; where
it is not, the phrase refuses rather than handing back a fabricated Monday.
"""


import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, nomatch, parse, start


@pytest.mark.parametrize("n", [2, 3])
def test_postposed_acum_reads_months(n):
    """"2 luni acum" reaches the same month-offset verdict as the canonical
    "acum 2 luni" -- not the N-th Monday back."""
    assert start(f"{n} luni acum") == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("n", [2, 3])
def test_leading_acum_reads_months(n):
    """The canonical shape, pinned here as the control the postposed forms
    must agree with."""
    assert start(f"acum {n} luni") == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("phrase", [
    "2 luni de la prezent", "3 luni din prezent",
])
def test_counted_luni_with_from_present_refuses(phrase):
    """The forward "<from> <present>" frame has no months reading wired for
    this locale, and the surface admits no counted-Monday reading -- so the
    phrase refuses instead of answering a Monday it cannot mean."""
    nomatch(phrase)


@pytest.mark.parametrize("phrase,remainder", [
    ("2 luni de la azi", "2 luni de la"), ("3 luni din azi", "3 luni din"),
])
def test_counted_luni_with_from_today_never_names_a_monday(phrase, remainder):
    """The deictic "azi" carries its own today reading; the count and the
    homographic surface stay visible in the remainder rather than being
    consumed into a fabricated Monday."""
    r = parse(phrase)
    assert r is not None
    assert r[0].start == ad(ANCHOR.replace(hour=0, minute=0))
    assert r[1] == remainder


@pytest.mark.parametrize("n,expected_day", [(2, 13), (3, 6)])
def test_counted_unambiguous_weekday_still_counts(n, expected_day):
    """"marți" (Tuesday) shares no surface with a unit, so the counted-weekday
    reading is untouched on both sides: the leading marker and the postposed
    one both step back N Tuesdays from the Tuesday anchor."""
    for phrase in (f"acum {n} marți", f"{n} marți acum"):
        s = start(phrase)
        assert s.weekday() == 1
        assert s.day == expected_day
