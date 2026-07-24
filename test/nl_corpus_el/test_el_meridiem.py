"""Greek π.μ. / μ.μ. clock times -- the abbreviated meridiem markers.

"π.μ." (προ μεσημβρίας, "before midday") and "μ.μ." (μετά μεσημβρίαν, "after
midday") are the standard written Greek meridiem abbreviations -- Λεξικό της
Κοινής Νεοελληνικής (Ίδρυμα Μανόλη Τριανταφυλλίδη, ΙΝΣ/ΑΠΘ 1998) s.v. "π.μ." /
"μ.μ."; Triantafyllidis, Νεοελληνική Γραμματική §403 (time expressions).  All
three renderings a Greek speaker actually types are covered: tight-dotted
("μ.μ."), spaced-dotted ("μ. μ.") and the informal dot-less ("μμ").

The regression these tests guard is a SILENT WRONG: the shipped dotted
vocabulary could never match a token (the tokenizer discards dots), so the
marker fell into the remainder and every p.m. time resolved twelve hours
early -- "3 μ.μ." read as 03:00.  Every case therefore asserts the exact
time AND that nothing is left over.

A time at or before the 13:04 anchor rolls to the next day (prefer_future);
the oracle uses independent arithmetic.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start


def _next_time(h, mi=0):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


PM = ["μ.μ.", "μ. μ.", "μμ"]
AM = ["π.μ.", "π. μ.", "πμ"]


@pytest.mark.parametrize("marker", PM)
@pytest.mark.parametrize("hour", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
def test_pm_hours(hour, marker):
    text = f"{hour} {marker}"
    assert start(text) == _next_time(hour + 12)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("marker", AM)
@pytest.mark.parametrize("hour", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
def test_am_hours(hour, marker):
    text = f"{hour} {marker}"
    assert start(text) == _next_time(hour)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("marker", PM)
def test_twelve_pm_is_noon(marker):
    """12 μ.μ. == 12:00 midday, matching the engine's English "12 pm"."""
    assert start(f"12 {marker}") == _next_time(12)


@pytest.mark.parametrize("marker", AM)
def test_twelve_am_is_midnight(marker):
    """12 π.μ. == 00:00 midnight, matching the engine's English "12 am"."""
    assert start(f"12 {marker}") == _next_time(0)


@pytest.mark.parametrize("text,h", [
    ("στη 3 μ. μ.", 15),
    ("στις 3 μ.μ.", 15),
    ("στις 9 π.μ.", 9),
    ("στις 11 μ.μ.", 23),
    ("το ραντεβού είναι στις 5 μ.μ.", 17),
    ("ξυπνάω στις 7 π.μ.", 7),
])
def test_in_a_sentence(text, h):
    assert start(text) == _next_time(h)


def test_bare_hour_without_marker_is_not_a_clock_time():
    """The meridiem is mandatory in the bare "HOUR MERIDIEM" order -- a lone
    digit must not silently become a clock time."""
    r = parse("3")
    assert r is None or r[0].start != _next_time(3)
